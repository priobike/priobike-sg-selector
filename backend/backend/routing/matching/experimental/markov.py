import hashlib
import heapq
import json
import math
import os
from collections import defaultdict
from functools import cached_property
from multiprocessing.pool import ThreadPool
from typing import Dict, List, Tuple, Union

from django.conf import settings
from django.contrib.gis.db.models.aggregates import Collect
from django.contrib.gis.db.models.fields import LineStringField
from django.contrib.gis.geos import LineString, MultiLineString
from django.contrib.gis.geos.point import Point
from django.db.models import F
from django.db.models.functions.comparison import Cast
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.models import SG


class MarkovModelNode:
    def __init__(self, id: str, sg: Union[SG, None], sigma_z: float, x: Point, z: Point):
        """
        Initialize the Markov model node.

        For a description about the terminology, see the paper:
        "Hidden Markov Map Matching Through Noise and Sparseness" by Newson and Krumm
        Available under: https://doi.org/10.1145/1653771.1653818

        :param id: The id of the node. Should be "start" or "end" or the SG ID.

        :param sg: The SG for the node. Is None if the node is the start or end node.

        :param sigma_z: In the paper, `sigma_z` is the standard deviation of the
        GPS measurements. In our implementation, `sigma_z` is the standard deviation
        of the route points.

        :param x: `x` points are the closest points on the road piece in the paper.
        The road pieces are the sg segments in our application.

        :param z: `z` points are the closest points on the GPS measurements in the
        paper. The GPS measurements are the route points in our application.
        """
        self.id = id
        self.sg = sg
        # TODO: Try to evaluate the sigma_z parameter statistically.
        self.sigma_z = sigma_z
        # Make sure that we use the correct projection
        projection = settings.METRICAL
        self.x = x.transform(projection, clone=True)
        self.z = z.transform(projection, clone=True)

    def __repr__(self):
        return f"{self.sg}"

    @cached_property
    def emission_probability(self) -> float:
        """
        The emission probability of the node in the Markov model.

        The emission probability tells that if the route point is closer
        to the sg point, it is more likely to be a match in the Markov chain.

        An exponential probability distribution is used.
        See the paper: https://doi.org/10.1145/1653771.1653818
        """
        c = 1 / (self.sigma_z * math.sqrt(2 * math.pi))
        great_circle_distance = self.z.distance(self.x)
        p = c * math.exp(-great_circle_distance**2)
        return p

    def __lt__(self, other):
        return self.id < other.id


def calc_route_distance(origin: MarkovModelNode, target: MarkovModelNode) -> float:
    """
    Calculate the route distance between two nodes.

    The route distance is the distance between the two nodes
    when using the road network as described in the paper.
    Since we use the SG geometries as roads, in our implementation,
    the route distance is the distance between the two nodes
    when using the sg geometries.
    """
    start_point = origin.x # Point on the SG
    end_point = target.x # Point on the SG

    # Make sure we use the correct projection
    projection = settings.METRICAL
    origin_sg_geom = origin.sg.geometry.transform(projection, clone=True) if origin.sg else None
    target_sg_geom = target.sg.geometry.transform(projection, clone=True) if target.sg else None

    if origin.sg is not None and target.sg is not None:
        if origin.sg.id == target.sg.id:
            # If both nodes are on the same sg, the route distance is
            # (start_point -> end_point)
            start_point_m = origin_sg_geom.project(start_point)
            end_point_m = target_sg_geom.project(end_point)

            route_distance = abs(end_point_m - start_point_m)
        else:
            # If both nodes are on different sg, the route distance is
            # (start_point -> end_of_origin_sg) -> (start_of_target_sg -> end_point)
            end_of_origin_sg = origin_sg_geom.interpolate_normalized(1)
            start_of_target_sg = target_sg_geom.interpolate_normalized(0)

            start_point_m = origin_sg_geom.project(start_point)
            end_of_origin_sg_m = origin_sg_geom.length
            dist_1 = abs(end_of_origin_sg_m - start_point_m)

            transition_dist = end_of_origin_sg.distance(start_of_target_sg)

            start_of_target_sg_m = 0
            end_point_m = target_sg_geom.project(end_point)
            dist_2 = abs(end_point_m - start_of_target_sg_m)

            route_distance = dist_1 + transition_dist + dist_2

    elif origin.sg is not None:
        # If only the origin node is on a sg, the route distance is
        # (start_point -> end_of_origin_sg) -> end_point
        end_of_origin_sg = origin_sg_geom.interpolate_normalized(1)

        start_point_m = origin_sg_geom.project(start_point)
        end_of_origin_sg_m = origin_sg_geom.length
        dist_1 = abs(end_of_origin_sg_m - start_point_m)

        dist_2 = end_of_origin_sg.distance(end_point)

        route_distance = dist_1 + dist_2

    elif target.sg is not None:
        # If only the target node is on a sg, the route distance is
        # start_point -> (start_of_target_sg -> end_point)
        start_of_target_sg = target_sg_geom.interpolate_normalized(0)

        dist_1 = start_point.distance(start_of_target_sg)

        start_of_target_sg_m = 0
        end_point_m = target_sg_geom.project(end_point)
        dist_2 = abs(end_point_m - start_of_target_sg_m)

        route_distance = dist_1 + dist_2

    else:
        # If both nodes are not on a sg, the route distance is
        # start_point -> end_point
        route_distance = start_point.distance(end_point)

    return route_distance


class MarkovModelEdge:
    def __init__(self, beta: float, origin: MarkovModelNode, target: MarkovModelNode):
        """
        Initialize the Markov model edge.

        For a description about the terminology, see the paper:
        "Hidden Markov Map Matching Through Noise and Sparseness" by Newson and Krumm
        Available under: https://doi.org/10.1145/1653771.1653818

        :param beta: The beta parameter of the Markov model. Describes the
        difference between route distances and great circle distances.

        :param origin: The origin node of the edge.
        :param target: The target node of the edge.
        """
        self.beta = beta
        self.origin = origin
        self.target = target

    @cached_property
    def transition_probability(self) -> float:
        """
        Compute the transition probability of the edge.

        For more information, see the paper: https://doi.org/10.1145/1653771.1653818
        """
        route_dist = calc_route_distance(self.origin, self.target)
        great_circle_dist = self.origin.z.distance(self.target.z)
        delta = abs(great_circle_dist - route_dist)
        c = 1 / self.beta
        p = c * math.exp(-delta / self.beta)
        return p


class MarkovModel:
    def __init__(self, beta: float, nodes: List[MarkovModelNode]):
        self.beta = beta

        assert len(nodes[0]) == 1
        self.start_node = nodes[0][0]
        assert(len(nodes[-1])) == 1
        self.end_node = nodes[-1][0]

        self.nodes = nodes

    @classmethod
    def build_model(cls, sigma_z: float, beta: float, route_points: List[Point], crossing_sgs: List[SG]) -> 'MarkovModel':
        """
        Build a Markov model (DAG) from the given route points and crossing SGs.
        """
        # See https://github.com/valhalla/valhalla/blob/master/docs/meili/algorithms.md
        nodes = []
        # Add the route start point to the DAG as the initial layer
        start_point = MarkovModelNode("start", None, sigma_z, route_points[0], route_points[0])
        nodes.append([start_point])

        for point_on_route in route_points:
            # Project the point onto each SG
            layer_nodes = []
            for sg in crossing_sgs:
                geometry = sg.geometry.transform(settings.METRICAL, clone=True)
                fraction = geometry.project_normalized(point_on_route)
                point_on_sg = geometry.interpolate_normalized(fraction)
                node = MarkovModelNode(sg.id, sg, sigma_z, point_on_sg, point_on_route)
                layer_nodes.append(node)
            nodes.append(layer_nodes)

        # Add the route end point to the DAG as the final layer
        end_point = MarkovModelNode("end", None, sigma_z, route_points[-1], route_points[-1])
        nodes.append([end_point])

        # Build the Markov model
        return cls(beta, nodes)

    @cached_property
    def adjacency_list(self) -> Dict[MarkovModelNode, List[MarkovModelNode]]:
        """
        Create the adjacency list of the Markov model.
        """
        adjacency_list = defaultdict(list)
        for layer_1, layer_2 in zip(self.nodes[:-1], self.nodes[1:]):
            # Layers are fully connected
            for node_1 in layer_1:
                for node_2 in layer_2:
                    adjacency_list[node_1].append(node_2)
        adjacency_list[self.end_node] = []
        return adjacency_list

    def viterbi(self) -> List[str]:
        """
        Find the most probable path in the graph using Viterbi's algorithm.

        The path will be returned as a list of ordered sg ids.
        """
        s: MarkovModelNode = self.start_node
        t: MarkovModelNode = self.end_node
        joint_prob = {}
        for u in self.adjacency_list:
            joint_prob[u] = 0
        predecessor = {}
        fifo_queue = []

        fifo_queue.append(s)
        joint_prob[s] = s.emission_probability
        predecessor[s] = None
        while fifo_queue:
            u = fifo_queue.pop(0)
            if u == t:
                break
            for v in self.adjacency_list[u]:
                # Relaxation
                edge = MarkovModelEdge(self.beta, u, v)
                new_prob = joint_prob[u] * edge.transition_probability * v.emission_probability
                if joint_prob[v] < new_prob:
                    joint_prob[v] = new_prob
                    predecessor[v] = u
                if v not in fifo_queue:
                    fifo_queue.append(v)
        
        # Reconstruct the path
        path = []
        curr_v = t
        while curr_v != s:
            path.append(curr_v)
            try:
                curr_v = predecessor[curr_v]
            except KeyError:
                return []
        path.append(s)

        reversed_path = path[::-1] # Reverse the reconstructed path
        return reversed_path


class MarkovMatcher(RouteMatcher):
    def __init__(self, crossing_padding=10, sigma_z=4.07, beta=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crossing_padding = crossing_padding
        self.sigma_z = sigma_z
        self.beta = beta

    def process_crossing(self, crossing, sgs, route) -> List[str]:
        # Use the Extent query to annotate the extent of each crossing
        # Note: the cast is necessary because the geometry is a geography type
        crossing_id = crossing["crossing_id"]
        crossing_sgs = sgs.filter(sgmetadata__traffic_lights_id=crossing_id)
        # Use only the sgs that were selected beforehand in the sgs queryset
        crossing_geom = crossing_sgs \
            .annotate(cast_geometry=Cast("geometry", LineStringField())) \
            .aggregate(geom=Collect("cast_geometry"))
        crossing_bound = crossing_geom["geom"].envelope \
            .transform(settings.METRICAL, clone=True) \
            .buffer(self.crossing_padding) \
            .transform(self.system, clone=True)

        # Get the route section that is within the crossing bound
        route_section = crossing_bound.intersection(route).transform(settings.METRICAL, clone=True)

        if isinstance(route_section, LineString):
            route_points = [
                Point(coord, srid=route_section.srid)
                for coord in route_section.coords
            ]
        elif isinstance(route_section, MultiLineString):
            route_points = []
            for line in route_section:
                route_points.extend([
                    Point(coord, srid=line.srid)
                    for coord in line.coords
                ])
        else:
            return []

        if len(route_section.coords) < 2:
            return []

        points_on_route = route_points.copy()
        while len(points_on_route) > 1:
            model = MarkovModel.build_model(self.sigma_z, self.beta, points_on_route, crossing_sgs)
            best_path: List[MarkovModelNode] = model.viterbi()[1:][:-1]
            if not best_path:
                # Remove the first route point
                points_on_route.pop(0)
                continue
            return [node.id for node in best_path]
        return []

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        sgs, route = super().matches(sgs, route)
        sgs_ids = sgs.values_list("pk", flat=True)

        # Group by the associated crossing
        crossings = sgs \
            .select_related("sgmetadata") \
            .annotate(crossing_id=F("sgmetadata__traffic_lights_id")) \
            .values("crossing_id") \
            .distinct() \
            .order_by("crossing_id")

        sg_ids = []

        pool = ThreadPool(processes=1)
        threads = []
        for crossing in crossings:
            thread = pool.apply_async(self.process_crossing, (crossing, sgs, route))
            threads.append(thread)
        for thread in threads:
            sg_ids.extend(thread.get())

        return sgs.filter(id__in=sg_ids), route

import hashlib
import heapq
import json
import math
from multiprocessing.pool import ThreadPool
import os
from collections import defaultdict
from functools import cached_property
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
from routing.models import LSA


class MarkovModelNode:
    def __init__(self, id: str, lsa: Union[LSA, None], sigma_z: float, x: Point, z: Point):
        """
        Initialize the Markov model node.

        For a description about the terminology, see the paper:
        "Hidden Markov Map Matching Through Noise and Sparseness" by Newson and Krumm
        Available under: https://doi.org/10.1145/1653771.1653818

        :param id: The id of the node. Should be "start" or "end" or the LSA ID.

        :param lsa: The LSA for the node. Is None if the node is the start or end node.

        :param sigma_z: In the paper, `sigma_z` is the standard deviation of the
        GPS measurements. In our implementation, `sigma_z` is the standard deviation
        of the route points.

        :param x: `x` points are the closest points on the road piece in the paper.
        The road pieces are the lsa segments in our application.

        :param z: `z` points are the closest points on the GPS measurements in the
        paper. The GPS measurements are the route points in our application.
        """
        self.id = id
        self.lsa = lsa
        # TODO: Try to evaluate the sigma_z parameter statistically.
        self.sigma_z = sigma_z
        # Make sure that we use the correct projection
        projection = settings.METRICAL
        self.x = x.transform(projection, clone=True)
        self.z = z.transform(projection, clone=True)

    def __repr__(self):
        return f"{self.lsa}"

    @cached_property
    def emission_probability(self) -> float:
        """
        The emission probability of the node in the Markov model.

        The emission probability tells that if the route point is closer
        to the lsa point, it is more likely to be a match in the Markov chain.

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
    Since we use the LSA geometries as roads, in our implementation,
    the route distance is the distance between the two nodes
    when using the lsa geometries.
    """
    start_point = origin.x # Point on the LSA
    end_point = target.x # Point on the LSA

    # Make sure we use the correct projection
    projection = settings.METRICAL
    origin_lsa_geom = origin.lsa.geometry.transform(projection, clone=True) if origin.lsa else None
    target_lsa_geom = target.lsa.geometry.transform(projection, clone=True) if target.lsa else None

    if origin.lsa is not None and target.lsa is not None:
        if origin.lsa.id == target.lsa.id:
            # If both nodes are on the same lsa, the route distance is
            # (start_point -> end_point)
            start_point_m = origin_lsa_geom.project(start_point)
            end_point_m = target_lsa_geom.project(end_point)

            route_distance = abs(end_point_m - start_point_m)
        else:
            # If both nodes are on different lsa, the route distance is
            # (start_point -> end_of_origin_lsa) -> (start_of_target_lsa -> end_point)
            end_of_origin_lsa = origin_lsa_geom.interpolate_normalized(1)
            start_of_target_lsa = target_lsa_geom.interpolate_normalized(0)

            start_point_m = origin_lsa_geom.project(start_point)
            end_of_origin_lsa_m = origin_lsa_geom.length
            dist_1 = abs(end_of_origin_lsa_m - start_point_m)

            transition_dist = end_of_origin_lsa.distance(start_of_target_lsa)

            start_of_target_lsa_m = 0
            end_point_m = target_lsa_geom.project(end_point)
            dist_2 = abs(end_point_m - start_of_target_lsa_m)

            route_distance = dist_1 + transition_dist + dist_2

    elif origin.lsa is not None:
        # If only the origin node is on a lsa, the route distance is
        # (start_point -> end_of_origin_lsa) -> end_point
        end_of_origin_lsa = origin_lsa_geom.interpolate_normalized(1)

        start_point_m = origin_lsa_geom.project(start_point)
        end_of_origin_lsa_m = origin_lsa_geom.length
        dist_1 = abs(end_of_origin_lsa_m - start_point_m)

        dist_2 = end_of_origin_lsa.distance(end_point)

        route_distance = dist_1 + dist_2

    elif target.lsa is not None:
        # If only the target node is on a lsa, the route distance is
        # start_point -> (start_of_target_lsa -> end_point)
        start_of_target_lsa = target_lsa_geom.interpolate_normalized(0)

        dist_1 = start_point.distance(start_of_target_lsa)

        start_of_target_lsa_m = 0
        end_point_m = target_lsa_geom.project(end_point)
        dist_2 = abs(end_point_m - start_of_target_lsa_m)

        route_distance = dist_1 + dist_2

    else:
        # If both nodes are not on a lsa, the route distance is
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
    def build_model(cls, sigma_z: float, beta: float, route_points: List[Point], crossing_lsas: List[LSA]) -> 'MarkovModel':
        """
        Build a Markov model (DAG) from the given route points and crossing LSAs.
        """
        # See https://github.com/valhalla/valhalla/blob/master/docs/meili/algorithms.md
        nodes = []
        # Add the route start point to the DAG as the initial layer
        start_point = MarkovModelNode("start", None, sigma_z, route_points[0], route_points[0])
        nodes.append([start_point])

        for point_on_route in route_points:
            # Project the point onto each LSA
            layer_nodes = []
            for lsa in crossing_lsas:
                geometry = lsa.geometry.transform(settings.METRICAL, clone=True)
                fraction = geometry.project_normalized(point_on_route)
                point_on_lsa = geometry.interpolate_normalized(fraction)
                node = MarkovModelNode(lsa.id, lsa, sigma_z, point_on_lsa, point_on_route)
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

        The path will be returned as a list of ordered lsa ids.
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

    def process_crossing(self, crossing, lsas, route) -> List[str]:
        # Use the Extent query to annotate the extent of each crossing
        # Note: the cast is necessary because the geometry is a geography type
        crossing_id = crossing["crossing_id"]
        crossing_lsas = lsas.filter(lsametadata__traffic_lights_id=crossing_id)
        # Use only the lsas that were selected beforehand in the lsas queryset
        crossing_geom = crossing_lsas \
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
            model = MarkovModel.build_model(self.sigma_z, self.beta, points_on_route, crossing_lsas)
            best_path: List[MarkovModelNode] = model.viterbi()[1:][:-1]
            if not best_path:
                # Remove the first route point
                points_on_route.pop(0)
                continue
            return [node.id for node in best_path]
        return []

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        lsas, route = super().matches(lsas, route)
        lsas_ids = lsas.values_list("pk", flat=True)

        # Group by the associated crossing
        crossings = lsas \
            .select_related("lsametadata") \
            .annotate(crossing_id=F("lsametadata__traffic_lights_id")) \
            .values("crossing_id") \
            .distinct() \
            .order_by("crossing_id")

        lsa_ids = []

        pool = ThreadPool(processes=1)
        threads = []
        for crossing in crossings:
            thread = pool.apply_async(self.process_crossing, (crossing, lsas, route))
            threads.append(thread)
        for thread in threads:
            lsa_ids.extend(thread.get())

        return lsas.filter(id__in=lsa_ids), route


def _write_debug_geojson(route_section, crossing_id, crossing_bound, crossing_lsas, best_path):
    route_hash = hashlib.sha1(route_section.wkb).hexdigest()

    features = [
        {
            "type": "Feature",
            "geometry": json.loads(route_section.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "stroke": "black",
                "stroke-width": 4,
                "stroke-opacity": 1,
            },
        } if route_section else None,
        {
            "type": "Feature",
            "geometry": json.loads(crossing_bound.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "fill-opacity": 0.1,
                "stroke": "black",
                "stroke-width": 2,
                "stroke-opacity": 1,
            },
        },
    ]
    features += [
        {
            "type": "Feature",
            "geometry": json.loads(lsa.geometry.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "stroke": "#00ff00",
                "stroke-width": 4,
                "stroke-opacity": 1,
            },
        } for lsa in crossing_lsas
    ]
    # Build a geojson object from the best path
    points = []
    for node in best_path:
        points.append(node.x.transform(settings.LONLAT, clone=True)[:2])
    if points:
        features.append({
            "type": "Feature",
            "geometry": json.loads(LineString(points, srid=settings.LONLAT).geojson),
            "properties": {
                "stroke": "#ff0000",
                "stroke-width": 2,
                "stroke-opacity": 1,
            },
        })
    for node in best_path:
        line = LineString([
            node.x.transform(settings.LONLAT, clone=True)[:2], 
            node.z.transform(settings.LONLAT, clone=True)[:2]
        ], srid=settings.LONLAT)                
        features.append({
            "type": "Feature",
            "geometry": json.loads(line.geojson),
            "properties": {
                "stroke": "black",
                "stroke-width": 1,
                "stroke-opacity": 1,
            },
        })

    collection = {
        "type": "FeatureCollection",
        "features": [f for f in features if f is not None],
    }

    # Make a directory for the route
    route_dir = "debug/{}".format(route_hash)
    if not os.path.exists(route_dir):
        os.makedirs(route_dir)

    with open(f"{route_dir}/crossing-{crossing_id}.json", "w") as f:
        json.dump(collection, f, indent=2)

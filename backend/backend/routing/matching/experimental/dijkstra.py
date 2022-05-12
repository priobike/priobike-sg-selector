import heapq
import json
import os
from collections import defaultdict
from multiprocessing.pool import ThreadPool
from typing import Dict, List, Tuple, Union

from django.conf import settings
from django.contrib.gis.db.models.aggregates import Collect
from django.contrib.gis.db.models.fields import LineStringField
from django.contrib.gis.geos import LineString, MultiLineString
from django.db.models import F
from django.db.models.functions.comparison import Cast
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.models import SG


def dijkstra(graph: Dict[str, List[Tuple[str, float]]], start: str, end: str) -> List[str]:
    # The heap is structured as: (cost, id)
    heap = [(0, start)]
    # The visited nodes are stored as: id -> cost
    visited = {start: 0}
    # The path ist stored as: id -> [id, ...]
    path = {start: [start]}

    while heap:
        cost, current = heapq.heappop(heap)
        if current == end:
            break
        for neighbor, neighbor_cost in graph[current]:
            if neighbor not in visited or visited[neighbor] > cost + neighbor_cost:
                visited[neighbor] = cost + neighbor_cost
                path[neighbor] = path[current] + [neighbor]
                heapq.heappush(heap, (visited[neighbor], neighbor))
    
    return path[end]


class DijkstraMatcher(RouteMatcher):
    """
    A Dijkstra matcher with a simple approach to the cost calculation.

    Unlike the strict dijkstra matcher, which computes the cost of transitioning
    between the route and the respective SG, this matcher computes the cost of
    transitioning between the route and the respective SG, and the cost of
    transitioning between the SG and the next SG. Unlike the strict dijkstra
    matcher, this matcher will use direct distances instead of route-bound
    distances over the nearest points.

    Note that because of the above, this matcher will presumably have
    more false positives and less false negatives than the strict dijkstra matcher.
    """

    def __init__(self, crossing_padding=20, offsg_penalty=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crossing_padding = crossing_padding
        self.offsg_penalty = offsg_penalty

    def process_crossing(self, crossing, sgs, route) -> List[str]:
        # Use the Extent query to annotate the extent of each crossing
        # Note: the cast is necessary because the geometry is a geography type
        crossing_id = crossing["crossing_id"]
        crossing_sgs = sgs.filter(sgmetadata__traffic_lights_id=crossing_id)
        crossing_geom = crossing_sgs \
            .annotate(cast_geometry=Cast("geometry", LineStringField())) \
            .aggregate(geom=Collect("cast_geometry"))
        crossing_bound = crossing_geom["geom"].envelope \
            .transform(settings.METRICAL, clone=True) \
            .buffer(self.crossing_padding) \
            .transform(self.system, clone=True)

        # Get the route section that is within the crossing bound
        route_section = crossing_bound.intersection(route).transform(settings.METRICAL, clone=True)

        if len(route_section.coords) < 2:
            return []

        graph = self.create_graph(crossing_sgs, route_section)
        shortest_path = dijkstra(graph, "start", "end")
        return shortest_path[1:-1] # Remove start and end

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        sgs, route = super().matches(sgs, route)

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

    def create_graph(self, sgs: List[SG], route: Union[LineString, MultiLineString], system=settings.METRICAL):
        # The graph ist structured as: id -> [(id, cost)]
        # Note that id is "start" or "end" for the start and end node
        graph = defaultdict(list)

        system_route = route.transform(system, clone=True)

        route_start_point = system_route.interpolate_normalized(0)
        route_end_point = system_route.interpolate_normalized(1)

        for sg in sgs:
            sg_geometry = sg.geometry.transform(system, clone=True)
            sg_start_point = sg_geometry.interpolate_normalized(0)
            sg_end_point = sg_geometry.interpolate_normalized(1)

            # The route start point is connected to all sgs
            # Cost is: route_start_point -> sg_start_point -> sg_end_point
            start_point_to_sg_cost = (self.offsg_penalty * sg_start_point.distance(route_start_point)) + sg_geometry.length
            graph["start"].append((sg.id, start_point_to_sg_cost))

            # All sgs are connected to the route end point
            # Cost is: sg_end_point -> route_end_point
            sg_to_end_point_cost = self.offsg_penalty * sg_end_point.distance(route_end_point)
            graph[sg.id].append(("end", sg_to_end_point_cost))

            for other_sg in sgs:
                if other_sg == sg:
                    continue

                other_sg_geometry = other_sg.geometry.transform(system, clone=True)
                other_sg_start_point = other_sg_geometry.interpolate_normalized(0)

                # The sgs are connected to each other
                # Cost is: sg_end_point -> other_sg_start_point -> other_sg_end_point
                sg_to_other_sg_cost = (self.offsg_penalty * sg_end_point.distance(other_sg_start_point)) + other_sg_geometry.length
                graph[sg.id].append((other_sg.id, sg_to_other_sg_cost))      

        # The start point is connected to the end point
        # Cost is: route_start_point -> route_end_point
        graph["start"].append(("end", self.offsg_penalty * system_route.length))
        
        return graph


class StrictDijkstraMatcher(DijkstraMatcher):
    """
    A Dijkstra matcher with a different approach to the cost calculation.

    The strict dijkstra matcher includes costs for the distance between the
    sgs and the route, so that paths from the route to the sgs are more
    expensive. To compute these costs, the nearest points of the sgs and the
    route are computed, as waypoints of leaving the route to get to the sg.

    Note that this matcher will prefer to stay on the route much more
    often than the regular dijkstra matcher. The number of false positives
    will presumably be lower, but the number of false negatives will be higher.
    """

    def create_graph(self, sgs: List[SG], route: Union[LineString, MultiLineString], system=settings.METRICAL):
        # The graph ist structured as: id -> [(id, cost)]
        # Note that id is "start" or "end" for the start and end node
        graph = defaultdict(list)

        system_route = route.transform(system, clone=True)

        for sg in sgs:
            sg_geometry = sg.geometry.transform(system, clone=True)
            sg_start_point = sg_geometry.interpolate_normalized(0)
            sg_end_point = sg_geometry.interpolate_normalized(1)

            # 1. The route start point is connected to all sgs
            # Cost is: route_start_point -1> closest_point_on_route -2> sg_start_point -3> sg_end_point
            _1_distance_1 = system_route.project(sg_start_point) * self.offsg_penalty
            _1_distance_2 = system_route.distance(sg_start_point) * self.offsg_penalty
            _1_distance_3 = sg_geometry.length
            graph["start"].append((sg.id, _1_distance_1 + _1_distance_2 + _1_distance_3))

            # 2. All sgs are connected to the route end point
            # Cost is: sg_end_point -1> closest_point_on_route -2> route_end_point
            _2_distance_1 = sg_end_point.distance(system_route) * self.offsg_penalty
            _2_distance_2 = (system_route.length - system_route.project(sg_end_point)) * self.offsg_penalty
            graph[sg.id].append(("end", _2_distance_1 + _2_distance_2))

            for other_sg in sgs:
                if other_sg == sg:
                    continue

                other_sg_geometry = other_sg.geometry.transform(system, clone=True)
                other_sg_start_point = other_sg_geometry.interpolate_normalized(0)

                # 3. The sgs are connected to each other
                # Cost is: sg_end_point -1> closest_point_on_route -2> closest_point_on_route -3> other_sg_start_point -4> other_sg_end_point
                _3_distance_1 = sg_end_point.distance(system_route) * self.offsg_penalty
                _3_distance_2 = abs(system_route.project(other_sg_start_point) - system_route.project(sg_end_point)) * self.offsg_penalty
                _3_distance_3 = system_route.distance(other_sg_start_point) * self.offsg_penalty
                _3_distance_4 = other_sg_geometry.length

                graph[sg.id].append((other_sg.id, _3_distance_1 + _3_distance_2 + _3_distance_3 + _3_distance_4))      

        # The start point is connected to the end point
        # Cost is: route_start_point -> route_end_point
        graph["start"].append(("end", system_route.length * self.offsg_penalty))
        
        return graph

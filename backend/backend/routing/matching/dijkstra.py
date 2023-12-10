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
from routing.models import LSA


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
    between the route and the respective LSA, this matcher computes the cost of
    transitioning between the route and the respective LSA, and the cost of
    transitioning between the LSA and the next LSA. Unlike the strict dijkstra
    matcher, this matcher will use direct distances instead of route-bound
    distances over the nearest points.

    Note that because of the above, this matcher will presumably have
    more false positives and less false negatives than the strict dijkstra matcher.
    """

    strict = False

    def __init__(self, crossing_padding=20, offlsa_penalty=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crossing_padding = crossing_padding
        self.offlsa_penalty = offlsa_penalty

    def process_crossing(self, crossing, lsas, route) -> List[str]:
        # Use the Extent query to annotate the extent of each crossing
        # Note: the cast is necessary because the geometry is a geography type
        crossing_id = crossing["crossing_id"]
        crossing_lsas = lsas.filter(lsametadata__traffic_lights_id=crossing_id)
        crossing_geom = crossing_lsas \
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

        graph, edges_coords = self.create_graph(crossing_lsas, route_section)
        shortest_path = dijkstra(graph, "start", "end")

        _write_debug_geojson(self.strict, route_section, crossing_id, crossing_bound, crossing_lsas, crossing_lsas.filter(id__in=shortest_path[1:-1]), "random-route", edges_coords)

        return shortest_path[1:-1] # Remove start and end

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        lsas, route = super().matches(lsas, route)

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

    def create_graph(self, lsas: List[LSA], route: Union[LineString, MultiLineString], system=settings.METRICAL):
        # The graph ist structured as: id -> [(id, cost)]
        # Note that id is "start" or "end" for the start and end node
        graph = defaultdict(list)

        edges_coords = []

        system_route = route.transform(system, clone=True)

        route_start_point = system_route.interpolate_normalized(0)
        route_end_point = system_route.interpolate_normalized(1)

        for lsa in lsas:
            lsa_geometry = lsa.geometry.transform(system, clone=True)
            lsa_start_point = lsa_geometry.interpolate_normalized(0)
            lsa_end_point = lsa_geometry.interpolate_normalized(1)

            # The route start point is connected to all lsas
            # Cost is: route_start_point -> lsa_start_point -> lsa_end_point
            start_point_to_lsa_cost = (self.offlsa_penalty * lsa_start_point.distance(route_start_point)) + lsa_geometry.length
            graph["start"].append((lsa.id, start_point_to_lsa_cost))
            edges_coords.append((lsa_start_point, lsa_end_point))

            # All lsas are connected to the route end point
            # Cost is: lsa_end_point -> route_end_point
            lsa_to_end_point_cost = self.offlsa_penalty * lsa_end_point.distance(route_end_point)
            graph[lsa.id].append(("end", lsa_to_end_point_cost))
            edges_coords.append((lsa_end_point, route_end_point))

            for other_lsa in lsas:
                if other_lsa == lsa:
                    continue

                other_lsa_geometry = other_lsa.geometry.transform(system, clone=True)
                other_lsa_start_point = other_lsa_geometry.interpolate_normalized(0)

                # The lsas are connected to each other
                # Cost is: lsa_end_point -> other_lsa_start_point -> other_lsa_end_point
                lsa_to_other_lsa_cost = (self.offlsa_penalty * lsa_end_point.distance(other_lsa_start_point)) + other_lsa_geometry.length
                graph[lsa.id].append((other_lsa.id, lsa_to_other_lsa_cost))   
                edges_coords.append((lsa_end_point, other_lsa_start_point))   

        # The start point is connected to the end point
        # Cost is: route_start_point -> route_end_point
        graph["start"].append(("end", self.offlsa_penalty * system_route.length))
        edges_coords.append((route_start_point, route_end_point))
        
        return graph, edges_coords


class StrictDijkstraMatcher(DijkstraMatcher):
    """
    A Dijkstra matcher with a different approach to the cost calculation.

    The strict dijkstra matcher includes costs for the distance between the
    lsas and the route, so that paths from the route to the lsas are more
    expensive. To compute these costs, the nearest points of the lsas and the
    route are computed, as waypoints of leaving the route to get to the lsa.

    Note that this matcher will prefer to stay on the route much more
    often than the regular dijkstra matcher. The number of false positives
    will presumably be lower, but the number of false negatives will be higher.
    """

    strict = True

    def create_graph(self, lsas: List[LSA], route: Union[LineString, MultiLineString], system=settings.METRICAL):
        # The graph ist structured as: id -> [(id, cost)]
        # Note that id is "start" or "end" for the start and end node
        graph = defaultdict(list)

        edges_coords = []

        system_route = route.transform(system, clone=True)

        for lsa in lsas:
            lsa_geometry = lsa.geometry.transform(system, clone=True)
            lsa_start_point = lsa_geometry.interpolate_normalized(0)
            lsa_end_point = lsa_geometry.interpolate_normalized(1)

            # 1. The route start point is connected to all lsas
            # Cost is: route_start_point -1> closest_point_on_route -2> lsa_start_point -3> lsa_end_point
            _1_distance_1 = system_route.project(lsa_start_point) * self.offlsa_penalty
            _1_distance_2 = system_route.distance(lsa_start_point) * self.offlsa_penalty
            _1_distance_3 = lsa_geometry.length
            graph["start"].append((lsa.id, _1_distance_1 + _1_distance_2 + _1_distance_3))
            closest_point_on_route = system_route.interpolate_normalized(system_route.project_normalized(lsa_start_point))
            edges_coords.append((closest_point_on_route, lsa_start_point))

            # 2. All lsas are connected to the route end point
            # Cost is: lsa_end_point -1> closest_point_on_route -2> route_end_point
            _2_distance_1 = lsa_end_point.distance(system_route) * self.offlsa_penalty
            _2_distance_2 = (system_route.length - system_route.project(lsa_end_point)) * self.offlsa_penalty
            graph[lsa.id].append(("end", _2_distance_1 + _2_distance_2))
            closest_point_on_route = system_route.interpolate_normalized(system_route.project_normalized(lsa_end_point))
            edges_coords.append((lsa_end_point, closest_point_on_route))

            for other_lsa in lsas:
                if other_lsa == lsa:
                    continue

                other_lsa_geometry = other_lsa.geometry.transform(system, clone=True)
                other_lsa_start_point = other_lsa_geometry.interpolate_normalized(0)

                # 3. The lsas are connected to each other
                # Cost is: lsa_end_point -1> closest_point_on_route -2> closest_point_on_route -3> other_lsa_start_point -4> other_lsa_end_point
                _3_distance_1 = lsa_end_point.distance(system_route) * self.offlsa_penalty
                _3_distance_2 = abs(system_route.project(other_lsa_start_point) - system_route.project(lsa_end_point)) * self.offlsa_penalty
                _3_distance_3 = system_route.distance(other_lsa_start_point) * self.offlsa_penalty
                _3_distance_4 = other_lsa_geometry.length

                graph[lsa.id].append((other_lsa.id, _3_distance_1 + _3_distance_2 + _3_distance_3 + _3_distance_4))
                closest_point_on_route_1 = system_route.interpolate_normalized(system_route.project_normalized(lsa_end_point))
                closest_point_on_route_2 = system_route.interpolate_normalized(system_route.project_normalized(other_lsa_start_point))
                edges_coords.append((lsa_end_point, closest_point_on_route_1))
                edges_coords.append((closest_point_on_route_1, closest_point_on_route_2))
                edges_coords.append((closest_point_on_route_2, other_lsa_start_point))

        # The start point is connected to the end point
        # Cost is: route_start_point -> route_end_point
        graph["start"].append(("end", system_route.length * self.offlsa_penalty))
        edges_coords.append((system_route.interpolate_normalized(0), system_route.interpolate_normalized(1)))
        
        return graph, edges_coords


def _write_debug_geojson(strict, route_section, crossing_id, crossing_bound, crossing_lsas, filtered_crossing_lsas, route_hash, edges_coords):
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(route_section.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "type": "route_section",
                "stroke": "black",
                "stroke-width": 4,
                "stroke-opacity": 1,
            },
        } if route_section else None,
        {
            "type": "Feature",
            "geometry": json.loads(crossing_bound.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "type": "crossing_bound",
                "fill-opacity": 0.1,
                "stroke": "black",
                "stroke-width": 2,
                "stroke-opacity": 1,
            },
        },
    ]

    # Plot the graph as well
    for (c1, c2) in edges_coords:
        c1_latlng, c2_latlng = c1.transform(settings.LONLAT, clone=True), c2.transform(settings.LONLAT, clone=True)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [c1_latlng.x, c1_latlng.y],
                    [c2_latlng.x, c2_latlng.y],
                ],
            },
            "properties": {
                "type": "graph_edge",
                "stroke": "#0000ff",
                "stroke-width": 2,
                "stroke-opacity": 1,
            },
        })

    features += [
        {
            "type": "Feature",
            "geometry": json.loads(lsa.geometry.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "type": "lsa_no_match",
                "stroke": "#ff0000",
                "stroke-width": 2,
                "stroke-opacity": 1,
            },
        } for lsa in crossing_lsas
    ]
    features += [
        {
            "type": "Feature",
            "geometry": json.loads(lsa.geometry.transform(settings.LONLAT, clone=True).geojson),
            "properties": {
                "type": "lsa_match",
                "stroke": "#00ff00",
                "stroke-width": 4,
                "stroke-opacity": 1,
            },
        } for lsa in filtered_crossing_lsas
    ]

    collection = {
        "type": "FeatureCollection",
        "features": [f for f in features if f is not None],
    }

    # Make a directory for the route
    if strict:   
        route_dir = "debug/strict/{}".format(route_hash)
    else:
        route_dir = "debug/default/{}".format(route_hash)
    if not os.path.exists(route_dir):
        os.makedirs(route_dir)

    with open(f"{route_dir}/crossing-{crossing_id}.json", "w") as f:
        json.dump(collection, f, indent=2)
from django.contrib.gis.measure import D
from django.contrib.gis.geos.linestring import LineString
from routing.matching.bearing import calc_bearing_diffs
from routing.matching.projection import project_onto_route

from routing.models import LSA

class MultiLaneMatcher:
    """
    Class for the multi lane SG matching algorithm.
    """
    
    def __init__(self, route: LineString):
        self.route = route
        
    def match(self, distance_to_route: int, bearing_diff: int):
        """
        Perform the multi lane matching based on proximity and bearing.
        """
        
        # First: Gather all SGs that are within a certain distance of the route.
        nearby_sgs = LSA.objects.filter(geometry__dwithin=(self.route, D(m=distance_to_route)))
        
        # Second: Filter the SGs by bearing.
        sg_ids_to_remove = set()
        for sg in nearby_sgs:
            sg_start = LineString(sg.ingress_geometry.coords[-2:])
            sg_start.srid = sg.ingress_geometry.srid
            sg_start_route_projection = project_onto_route(sg_start, self.route)
            
            bearing_diffs = calc_bearing_diffs(sg_start, sg_start_route_projection)
                       
            if bearing_diffs[0] > bearing_diff:
                sg_ids_to_remove.add(sg.id)
        
        nearby_sgs.exclude(id__in=sg_ids_to_remove)

        return nearby_sgs
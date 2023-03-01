from django.contrib.gis.measure import D
from django.contrib.gis.geos.linestring import LineString
from routing.matching.bearing import calc_bearing_diffs
from routing.matching.projection import project_onto_route
from routing.matching.bearing import get_bearing

from routing.models import LSA

class CrossingMatcher:
    """
    Class for the crossing SG matching algorithm.
    """
    
    def __init__(self, route: LineString):
        self.route = route
        
    def match(self):
        """
        Perform the bulk matching based on proximity and bearing.
        """
        
        # First: Gather all SGs that are within a 50m distance of the last waypoint of the route.
        nearby_sgs = LSA.objects.filter(geometry__dwithin=(self.route, D(m=20)))
        
        # Second: Filter the SGs by bearing. Only keep SGs where the bearing between the first two waypoints of the SG
        # is similar to the bearing of the last two waypoints of the route.
        sg_ids_to_remove = set()
        for sg in nearby_sgs:
            sg_start = LineString(sg.geometry.coords[:2])
            sg_start.srid = sg.geometry.srid
            sg_start_route_projection = project_onto_route(sg_start, self.route)
            
            bearing_diff = calc_bearing_diffs(sg_start, sg_start_route_projection)
            
            if bearing_diff[0] > 30:
                sg_ids_to_remove.add(sg.id)
        
        nearby_sgs.exclude(id__in=sg_ids_to_remove)

        return nearby_sgs
import json
import requests
import os

from django.conf import settings
from django.core.serializers import serialize
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from composer.models import Connection
from routing.matching.proximity import ProximityMatcher
from routing.models import LSA

from composer.models import Route
from routing.matching import get_matches
from routing.matching.ml.matcher import MLMatcher


def cross_origin(response):
    response["Access-Control-Allow-Origin"] = "*"
    return response
    
class SignalgroupsResource(View):
    def get(self, request):
        sgs = LSA.objects.all()
        
        ids = [lsa.id for lsa in sgs]

        connections = Connection.objects.filter(lsa__id__in=ids)
        
        geojson = serialize("geojson", connections, geometry_field="elevated_geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))
    
class SignalgroupsSegmentsResource(View):
    def get(self, request):
        sgs = LSA.objects.all()
        
        ids = [lsa.id for lsa in sgs]

        connections = Connection.objects.filter(lsa__id__in=ids)
            
        trips = []
        prev_waypoint = None
        for lsa in connections:
            for waypoint in lsa.elevated_geometry:
                if prev_waypoint is not None:
                    trips.append({
                        "waypoints": [{
                            "progress": 0,
                            "coordinates": prev_waypoint
                        }, {
                            "progress": 100,
                            "coordinates": waypoint
                        }]
                    })
                prev_waypoint = waypoint
            prev_waypoint = None
        trips_json = json.dumps(trips, indent=2 if settings.DEBUG else None)
        response = HttpResponse(trips_json, content_type="application/json")
        return cross_origin(response)
    
class MatchesResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
       
        body = { "route": [] }
        for point in route.geometry:
            body["route"].append({"lon": point[0], "lat": point[1], "alt": 0})
            
        params = request.GET
        matcher = str(params.get("matcher", "legacy"))
        
        print(">>>>>>>>>>>>>>>>>>> Used matcher for demo: " + matcher)
                
        r = requests.post(f'http://localhost:8000/routing/select?matcher={matcher}', json=body)
        ids = [sg.replace("hamburg/", "") for sg in r.json()["signalGroups"]]        

        """ geojson = serialize("geojson", matches, geometry_field="geometry") """
        return cross_origin(JsonResponse(ids, safe=False))

import time
from typing import List
import xml.etree.ElementTree as ET

import requests
from backend import settings
from ml_evaluation.utils_meta import get_filename
import numpy as np

from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState


class RouteStreets(FeatureExtractor):
    FEATURE_NAMES = [
        "street_changed",
        "street_didnt_changed"
    ]

    FEATURE_TYPES = [
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
    ]

    SUPPORTS_EXTENDED_PROJECTION = True

    def __init__(self, *args, **kwargs):
        """
        Initialize the route streets extractor.
        """
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_name_of_file():
        return get_filename()

    @staticmethod
    def get_statistics(features: List[List], labels: List[int]):
        """
        Used for the logs
        """

        features_binding_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 1])
        features_binding_not_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 0])

        statistic = {
            "binding_selected": {
                "route_street_changed_count": int(np.sum(features_binding_selected[:, 0])),
                "route_street_didnt_changed_count": int(np.sum(features_binding_selected[:, 1])),
                "ratio(route_street_changed_count/route_street_didnt_changed_count)":  f"{int(np.sum(features_binding_selected[:,0]) / int(np.sum(features_binding_selected[:,1]))) * 100}%"
            },
            "binding_not_selected": {
                "route_street_changed_count": int(np.sum(features_binding_not_selected[:, 0])),
                "route_street_didnt_changed_count": int(np.sum(features_binding_not_selected[:, 1])),
                "ratio(route_street_changed_count/route_street_didnt_changed_count)":  f"{int(np.sum(features_binding_not_selected[:,0]) / int(np.sum(features_binding_not_selected[:,1]))) * 100}%"
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        lsa_projected_linestring = featureExtractionState.lsa_projected_linestring if not featureExtractionState.config["extended_projections"]\
            else featureExtractionState.lsa_extended_projected_linestring

        lsa_projected_linestring_lon_lat = lsa_projected_linestring.transform(
            settings.LONLAT, clone=True)

        # Write GPX/XML for the map matching
        gpx = ET.Element("gpx")
        trk = ET.SubElement(gpx, "trk")
        trkseg = ET.SubElement(trk, "trkseg")

        for coordinate in lsa_projected_linestring_lon_lat.coords:
            ET.SubElement(trkseg, "trkpt", attrib={"lat": str(
                coordinate[1]), "lon": str(coordinate[0])})

        xml = ET.tostring(gpx, encoding='utf8', method='xml')

        # Perform Map Matching with the local GraphHopper API at port 8989
        headers = {'Content-type': 'application/xml', 'Accept': '*/*'}

        response = requests.post(
            "http://graphhopper:8989/match?profile=bike&details=street_name", data=xml, headers=headers)

        """ 
        Example response:
        
        {
            "hints": {},
            "info": {
                "copyrights": [
                    "GraphHopper",
                    "OpenStreetMap contributors"
                ],
                "took": 0
            },
            "paths": [
                {
                    "distance": 94.631,
                    "weight": 9.223372036854775E12,
                    "time": 18925,
                    "transfers": 0,
                    "points_encoded": true,
                    "bbox": [
                        10.051653,
                        53.511485,
                        10.052716,
                        53.511939
                    ],
                    "points": "wmreIskj|@SYeArE",
                    "instructions": [
                        {
                            "distance": 14.337,
                            "heading": 35.86,
                            "sign": 0,
                            "interval": [
                                0,
                                1
                            ],
                            "text": "Continue onto Peutestraße",
                            "time": 2867,
                            "street_name": "Peutestraße"
                        },
                        {
                            "distance": 80.294,
                            "sign": -2,
                            "interval": [
                                1,
                                2
                            ],
                            "text": "Turn left onto Müggenburger Straße",
                            "time": 16058,
                            "street_name": "Müggenburger Straße"
                        },
                        {
                            "distance": 0.0,
                            "sign": 4,
                            "last_heading": 298.9006225638479,
                            "interval": [
                                2,
                                2
                            ],
                            "text": "Arrive at destination",
                            "time": 0,
                            "street_name": ""
                        }
                    ],
                    "legs": [],
                    "details": {
                        "street_name": [
                            [
                                0,
                                1,
                                "Peutestraße"
                            ],
                            [
                                1,
                                2,
                                "Müggenburger Straße"
                            ]
                        ]
                    },
                    "ascend": 0.0,
                    "descend": 1.0,
                    "snapped_waypoints": ""
                }
            ],
            "map_matching": {
                "original_distance": 115.84688023136935,
                "distance": 94.63070803000674,
                "time": 18925
            }
        }
        """

        if response.status_code != 200:
            print(f'Route_id: {featureExtractionState.route.id}, LSA_id: {featureExtractionState.lsa.id} - Error during map matching process for "feature_route_streets.py".\nStatus code: {response.status_code}\nMessage: {response.json()}')
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 1])
        elif "street_name" not in response.json()["paths"][0]["details"]:
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 1])
        else:
            # For debugging:
            """ if len(response.json()["paths"]) > 1:
                print(f'Route_id: {route.id}, LSA_id: {lsa.id} - Größer eins') """

            response_street_details = response.json(
            )["paths"][0]["details"]["street_name"]

            street_changed = False
            if len(response_street_details) > 1:
                initial_street_name = response_street_details[0][2]
                for street in response_street_details:
                    if street[2] != initial_street_name:
                        # For debugging:
                        """ print(f'{initial_street_name} -> {street[2]}') """
                        street_changed = True
                        break
            
            # For debugging:
            """ if street_changed:
                print(f'Route_id: {route.id}, LSA_id: {lsa.id} - Success \n') """

            # Feature denoting whether the projected linestring changes streets at some point. (one hot encoded)
            # 1,0 = street changes
            # 0,1 = it stays on the same street
            if street_changed:
                featureExtractionState.features = np.append(
                    featureExtractionState.features, [1, 0])
            else:
                featureExtractionState.features = np.append(
                    featureExtractionState.features, [0, 1])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=(end - start), extra=None),
            Timing(base=-524, extra=None)
        ])

        return featureExtractionState

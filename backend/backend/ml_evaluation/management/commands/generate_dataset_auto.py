import gzip
import json
import os

import numpy as np
import pandas as pd
from composer.models import Route, RouteLSABinding
from django.conf import settings
from django.contrib.gis.geos import Point, fromstr
from django.contrib.gis.geos.linestring import LineString as GEOSLineString
from django.core.management.base import BaseCommand
from routing.matching import get_matches
from routing.matching.proximity import ProximityMatcher
from shapely import affinity, wkt
from shapely.geometry import LineString as ShapelyLineString
from tqdm import tqdm
from tsfresh import extract_relevant_features


def jiggle_linestring(geos_linestring: GEOSLineString):
    shapely_linestring: ShapelyLineString = wkt.loads(geos_linestring.wkt)
    
    rotation = np.random.uniform(-3, 3)
    shapely_linestring = affinity.rotate(shapely_linestring, rotation, origin='centroid')
    
    scale = np.random.uniform(0.975, 1.025)
    shapely_linestring = affinity.scale(shapely_linestring, scale, origin='centroid')
    
    translation_x_m = np.random.uniform(-5, 5)
    translation_y_m = np.random.uniform(-5, 5)
    # 111_111 m per degree is only a rough estimate but enough for small offsets
    translation_lat = translation_x_m / 111_111
    translation_lon = translation_y_m / 111_111
    shapely_linestring = affinity.translate(
        shapely_linestring,
        xoff=translation_lon,
        yoff=translation_lat,
    )

    return fromstr(shapely_linestring.wkt, srid=geos_linestring.srid)


N_AUGMENTED_SAMPLES_PER_SAMPLE = 1


class Command(BaseCommand):
    def handle(self, *args, **options):
        routes_with_bindings = Route.objects \
            .filter(bound_lsas__isnull=False) \
            .distinct()

        y = []
        X = []

        df_x = pd.DataFrame(columns=["id", "point_idx", "diff_lat", "diff_lon"])
        df_y = pd.Series(dtype=np.int8)
        for route in tqdm(routes_with_bindings, desc="Generating dataframe"):
            route_geometry = route.geometry.transform(settings.METRICAL, clone=True)
            
            bindings = RouteLSABinding.objects \
                .filter(route=route) \
                .select_related("lsa")

            all_lsas = get_matches(route.geometry, [ProximityMatcher(search_radius_m=15)])
            selected_lsas = set(b.lsa for b in bindings)

            for lsa in all_lsas:
                is_match = lsa in selected_lsas
                lsa_geometry = lsa.geometry.transform(settings.METRICAL, clone=True)
                augmented_geometries = [lsa_geometry]
                for _ in range(N_AUGMENTED_SAMPLES_PER_SAMPLE):
                    augmented_geometries.append(jiggle_linestring(lsa_geometry))
                
                for replica_idx, geometry in enumerate(augmented_geometries):
                    _id = f"{route.id}_{lsa.id}_{replica_idx}"
                    
                    for point_idx, lsa_coord in enumerate(geometry.coords):
                        point_on_lsa = Point(*lsa_coord[:2], srid=geometry.srid)
                        point_on_route = route_geometry.interpolate(route_geometry.project(point_on_lsa))
                        
                        df_x.loc[len(df_x)] = [
                            _id,
                            point_idx,
                            point_on_route.x - point_on_lsa.x,
                            point_on_route.y - point_on_lsa.y,
                        ]
                    
                    df_y.loc[_id] = int(is_match)
        
        features: pd.DataFrame = extract_relevant_features(
            df_x, df_y, 
            column_id="id", column_sort="point_idx", 
            disable_progressbar=False
        )
        # Get the features from the DataFrame column names
        feature_names = features.columns.values.tolist()
        
        X = features.values
        y = df_y.values

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)

        # Dump the dataset to disk
        dataset_path = os.path.join(settings.BASE_DIR, "../data/ml-dataset.json.gz")
        with gzip.open(dataset_path, "wb") as f:
            json_data = json.dumps({
                "feature_names": feature_names,
                "X": X, "y": y, 
            }, cls=NumpyEncoder)
            f.write(json_data.encode("utf-8"))
        print(f"Wrote dataset to {dataset_path}")

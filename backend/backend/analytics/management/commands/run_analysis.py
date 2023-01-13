import functools
from collections import defaultdict
from time import perf_counter
import os
import json
from routing.matching.ml.matcher import MLMatcher
from routing.matching.proximity import ProximityMatcher
from routing.matching.hypermodel import TopologicHypermodelMatcher
from composer.utils import get_routes_with_bindings
from analytics.models import Hit, RouteAnalysis, Run
from composer.models import RouteLSABinding
from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.conf import settings
from routing.matching import get_matches
from tqdm import tqdm

class Command(BaseCommand):
    help = """
        Compute how many lsas are found correctly
        with the matching algorithms.
    """ 

    def profile_algorithm(self, algorithm_name, matchers, route_data):
        run = Run.objects.create(algorithm_name=algorithm_name)
        
        routes_with_bindings = get_routes_with_bindings(route_data)
        
        constellations_right = {}
        constellations_false = {}
        route_errors_right = {}
        route_errors_false = {}

        for route in tqdm(routes_with_bindings, desc=f"\nProfiling algorithm {algorithm_name}"):
            bindings = RouteLSABinding.objects.filter(route=route).select_related("lsa")

            selected_lsas = [b.lsa.id for b in bindings]
            confirmed_lsas = [b.lsa.id for b in bindings if b.confirmed]

            # Get the matched lsas
            start = perf_counter()
            matched_lsas = get_matches(route.geometry, matchers)
            end = perf_counter()
            duration_seconds = end - start

            analysis = RouteAnalysis.objects.create(
                run=run,
                route=route,
                duration_seconds=duration_seconds
            )          
            
            matched_lsas = [lsa.id for lsa in matched_lsas]
            
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="tp") for lsa_id in
                set(matched_lsas) & set(selected_lsas)
            ])
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="tp_c") for lsa_id in
                set(matched_lsas) & set(confirmed_lsas)
            ])

            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="fn") for lsa_id in
                set(selected_lsas) - set(matched_lsas)
            ])
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="fn_c") for lsa_id in
                set(confirmed_lsas) - set(matched_lsas)
            ])

            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="fp") for lsa_id in
                set(matched_lsas) - set(selected_lsas)
            ])
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, lsa_id=lsa_id, key="fp_c") for lsa_id in
                set(matched_lsas) - set(confirmed_lsas)
            ])

            self.print_results(run)
            
            
            # Constellations and route error statistics
            for b in bindings:
                if b.lsa.id in matched_lsas and b.lsa.id in selected_lsas:
                    if b.corresponding_constellation is not None:
                        # RIGHT
                        # Constellations
                        if b.corresponding_constellation.custom_id not in constellations_right:
                            constellations_right[b.corresponding_constellation.custom_id] = 0
                        else:
                            constellations_right[b.corresponding_constellation.custom_id] = constellations_right[b.corresponding_constellation.custom_id] + 1
                    else:
                        # Constellations
                        if "Nicht ausgewaehlt" not in constellations_right:
                            constellations_right["Nicht ausgewaehlt"] = 0
                        else:
                            constellations_right["Nicht ausgewaehlt"] = constellations_right["Nicht ausgewaehlt"] + 1
                    if b.corresponding_route_error is not None:
                        # Route Errors
                        if b.corresponding_route_error.custom_id not in route_errors_right:
                            route_errors_right[b.corresponding_route_error.custom_id] = 0
                        else:
                            route_errors_right[b.corresponding_route_error.custom_id] = route_errors_right[b.corresponding_route_error.custom_id] + 1
                    else:
                        # Route Errors
                        if "Kein Fehler" not in route_errors_right:
                            route_errors_right["Kein Fehler"] = 0
                        else:
                            route_errors_right["Kein Fehler"] = route_errors_right["Kein Fehler"] + 1
                else:
                    if b.corresponding_constellation is not None:
                        # FALSE
                        # Constellations
                        if b.corresponding_constellation.custom_id not in constellations_false:
                            constellations_false[b.corresponding_constellation.custom_id] = 0
                        else:
                            constellations_false[b.corresponding_constellation.custom_id] = constellations_false[b.corresponding_constellation.custom_id] + 1
                    else:
                        # Constellations
                        if "Nicht ausgewaehlt" not in constellations_false:
                            constellations_false["Nicht ausgewaehlt"] = 0
                        else:
                            constellations_false["Nicht ausgewaehlt"] = constellations_false["Nicht ausgewaehlt"] + 1
                    if b.corresponding_route_error is not None:
                        # Route Errors
                        if b.corresponding_route_error.custom_id not in route_errors_false:
                            route_errors_false[b.corresponding_route_error.custom_id] = 0
                        else:
                            route_errors_false[b.corresponding_route_error.custom_id] = route_errors_false[b.corresponding_route_error.custom_id] + 1
                    else:
                        # Route Errors
                        if "Kein Fehler" not in route_errors_false:
                            route_errors_false["Kein Fehler"] = 0
                        else:
                            route_errors_false["Kein Fehler"] = route_errors_false["Kein Fehler"] + 1
                        
        constellations_right_ratio = {}
        route_errors_right_ratio = {}
        # Gather all possible constellations/route errors
        for key in constellations_right:
            if key not in constellations_right_ratio:
                constellations_right_ratio[key] = 0
        for key in constellations_false:
            if key not in constellations_right_ratio:
                constellations_right_ratio[key] = 0
        for key in route_errors_right:
            if key not in route_errors_right_ratio:
                route_errors_right_ratio[key] = 0
        for key in route_errors_false:
            if key not in route_errors_right_ratio:
                route_errors_right_ratio[key] = 0
        # Calculate ratios
        # Constellations
        for key in constellations_right_ratio:
            if key in constellations_right and key not in constellations_false:
                constellations_right_ratio[key] = 1.0
            elif key not in constellations_right and key in constellations_false:
                constellations_right_ratio[key] = 0.0
            else:
                constellations_right_ratio[key] = constellations_right[key] / (constellations_right[key] + constellations_false[key])
        # Route errors
        for key in route_errors_right_ratio:
            if key in route_errors_right and key not in route_errors_false:
                route_errors_right_ratio[key] = 1.0
            elif key not in route_errors_right and key in route_errors_false:
                route_errors_right_ratio[key] = 0.0
            else:
                route_errors_right_ratio[key] = route_errors_right[key] / (route_errors_right[key] + route_errors_false[key])
                
        constellations_and_route_error_statistics = {
            'constellations_right_ratio': constellations_right_ratio,
            'route_errors_right_ratio': route_errors_right_ratio,
            'constellations_right': constellations_right,
            'constellations_false': constellations_false,
            'route_errors_right': route_errors_right,
            'route_errors_false': route_errors_false
        }
        
        logs_path = "analytics/logs/"
        with open(os.path.join(settings.BASE_DIR, f"{logs_path}run_analysis_constellation_route_errors/constellation_route_error_logs_{algorithm_name}.json"), 'w', encoding='utf-8') as fp:
            json.dump(constellations_and_route_error_statistics, fp, indent=4)

        return run

    def print_results(self, run):
        tp = Hit.objects.filter(key="tp", run=run).count()
        fn = Hit.objects.filter(key="fn", run=run).count()
        fp = Hit.objects.filter(key="fp", run=run).count()
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

        tp_c = Hit.objects.filter(key="tp_c", run=run).count()
        fn_c = Hit.objects.filter(key="fn_c", run=run).count()
        fp_c = Hit.objects.filter(key="fp_c", run=run).count()
        precision_c = tp_c / (tp_c + fp_c) if tp_c + fp_c > 0 else 0
        recall_c = tp_c / (tp_c + fn_c) if tp_c + fn_c > 0 else 0
        f1_c = 2 * precision_c * recall_c / (precision_c + recall_c) if precision_c + recall_c > 0 else 0

        mean_exec_time = RouteAnalysis.objects \
            .filter(run=run) \
            .aggregate(mean_exec_time=Avg("duration_seconds")) \
            ["mean_exec_time"]

        # Print the results
        print(f"Results for run {run}:")
        print(f"TP: {tp}, FP: {fp}, FN: {fn}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1: {f1:.2f}")
        print(f"TP_C: {tp_c}, FP_C: {fp_c}, FN_C: {fn_c}")
        print(f"Precision_C: {precision_c:.2f}")
        print(f"Recall_C: {recall_c:.2f}")
        print(f"F1_C: {f1_c:.2f}")
        print(f"Mean execution time: {mean_exec_time}s")
        
    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies whether bindings based on OSM or DRN routes should be used.
        parser.add_argument("--route_data", type=str)

    def handle(self, *args, **options):
        print("Running analysis...")
        
        # Check if the path argument is valid
        if not options["route_data"]:
            raise Exception(
                "Please provide a route_data to specify which bindings should be used.")
            
        route_data = options["route_data"]
            
        if route_data != "osm" and route_data != "drn":
            raise Exception(
                "Please provide a valid value for the route_data option ('osm' or 'drn').")
        
        # Add strategies that should be analyized.
        # strategies = {"ml-drn": [ ProximityMatcher(search_radius_m=20), MLMatcher("drn") ]}
        strategies = {"topo": [ TopologicHypermodelMatcher.from_config_file() ]}

        runs = []
        for strategy_name, strategy in strategies.items():
            run = self.profile_algorithm(strategy_name, strategy, route_data)
            runs.append(run)

        if len(runs) > 1:
            self.compare_runs(runs)

    def compare_runs(self, runs):
        statistics = defaultdict(dict)
        for run in runs:
            for analysis in run.routeanalysis_set.all().order_by("route"):
                hits = analysis.hits.select_related("lsa")
                statistics[analysis.route.id][run.algorithm_name] = {
                    "tp": [hit.lsa.id for hit in hits.filter(key="tp")],
                    "tp_c": [hit.lsa.id for hit in hits.filter(key="tp_c")],
                    "fn": [hit.lsa.id for hit in hits.filter(key="fn")],
                    "fn_c": [hit.lsa.id for hit in hits.filter(key="fn_c")],
                    "fp": [hit.lsa.id for hit in hits.filter(key="fp")],
                    "fp_c": [hit.lsa.id for hit in hits.filter(key="fp_c")],
                }
       
        # Analysis for common and uncommon results between the strategies
        for route_id, strategy_stats in statistics.items():
            # Print the true positives that are common to all strategies
            tp = functools.reduce(lambda x, y: x & y, [
                set(strategy_stats[strategy_name]["tp"]) for strategy_name in strategy_stats 
            ])
            for strategy_name in strategy_stats:
                # Print the true positives that only exist in the current strategy
                tp_current = set(strategy_stats[strategy_name]["tp"])
                tp_current -= tp
                print(f"Route {route_id} has {len(tp_current)} true positives only in {strategy_name}")
            
            # Print the false positives that are common to all strategies
            fp = functools.reduce(lambda x, y: x & y, [
                set(strategy_stats[strategy_name]["fp"]) for strategy_name in strategy_stats
            ])
            for strategy_name in strategy_stats:
                # Print the false positives that only exist in the current strategy
                fp_current = set(strategy_stats[strategy_name]["fp"])
                fp_current -= fp
                print(f"Route {route_id} has {len(fp_current)} false positives only in {strategy_name}")

            # Print the false negatives that are common to all strategies
            fn = functools.reduce(lambda x, y: x & y, [
                set(strategy_stats[strategy_name]["fn"]) for strategy_name in strategy_stats
            ])
            for strategy_name in strategy_stats:
                # Print the false negatives that only exist in the current strategy
                fn_current = set(strategy_stats[strategy_name]["fn"])
                fn_current -= fn
                print(f"Route {route_id} has {len(fn_current)} false negatives only in {strategy_name}")

            bindings = RouteLSABinding.objects.filter(route_id=route_id).select_related("lsa")
            selected_lsas = [b.lsa.id for b in bindings]

            print(f"Route {route_id}: Common true positives: {len(tp)}, common false positives: {len(fp)}, common false negatives: {len(fn)}, selected LSAs: {len(selected_lsas)}")


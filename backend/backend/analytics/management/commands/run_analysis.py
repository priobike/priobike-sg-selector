import functools
from collections import defaultdict
from time import perf_counter

from analytics.models import Hit, RouteAnalysis, Run
from composer.models import Route, RouteSGBinding
from django.core.management.base import BaseCommand
from django.db.models import Avg
from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from tqdm import tqdm


class Command(BaseCommand):
    help = """
        Compute how many sgs are found correctly
        with the matching algorithms.
    """ 

    def profile_algorithm(self, algorithm_name, matchers):
        run = Run.objects.create(algorithm_name=algorithm_name)
        routes_with_bindings = Route.objects.filter(bound_sgs__isnull=False).order_by('pk').distinct()

        number_of_routes = routes_with_bindings.count()
        if number_of_routes == 0:
            print("No routes with bindings found.")
            return

        test_proportion = 0.2
        number_of_tests = int(number_of_routes * test_proportion)
        # Test dataset is the last 20% of the routes
        routes_with_bindings = routes_with_bindings[-number_of_tests:]

        for route in tqdm(routes_with_bindings, desc=f"\nProfiling algorithm {algorithm_name}"):
            bindings = RouteSGBinding.objects.filter(route=route).select_related("sg")

            selected_sgs = [b.sg.id for b in bindings]

            # Get the matched sgs
            start = perf_counter()
            matched_sgs = get_matches(route.geometry, matchers)
            end = perf_counter()
            duration_seconds = end - start

            analysis = RouteAnalysis.objects.create(
                run=run,
                route=route,
                duration_seconds=duration_seconds
            )

            matched_sgs = [sg.id for sg in matched_sgs]

            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, sg_id=sg_id, key="tp") for sg_id in
                set(matched_sgs) & set(selected_sgs)
            ])
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, sg_id=sg_id, key="fn") for sg_id in
                set(selected_sgs) - set(matched_sgs)
            ])
            Hit.objects.bulk_create([
                Hit(run=run, analysis=analysis, sg_id=sg_id, key="fp") for sg_id in
                set(matched_sgs) - set(selected_sgs)
            ])

            self.print_results(run)

        return run

    def print_results(self, run):
        tp = Hit.objects.filter(key="tp", run=run).count()
        fn = Hit.objects.filter(key="fn", run=run).count()
        fp = Hit.objects.filter(key="fp", run=run).count()
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

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
        print(f"Mean execution time: {mean_exec_time}s")

    def handle(self, *args, **options):
        print("Running analysis...")

        strategies = {
            "best": [ get_best_hypermodel() ],
        }

        runs = []
        for strategy_name, strategy in strategies.items():
            run = self.profile_algorithm(strategy_name, strategy)
            runs.append(run)

        if len(runs) > 1:
            self.compare_runs(runs)

    def compare_runs(self, runs):
        statistics = defaultdict(dict)
        for run in runs:
            for analysis in run.routeanalysis_set.all().order_by("route"):
                hits = analysis.hits.select_related("sg")
                statistics[analysis.route.id][run.algorithm_name] = {
                    "tp": [hit.sg.id for hit in hits.filter(key="tp")],
                    "fn": [hit.sg.id for hit in hits.filter(key="fn")],
                    "fp": [hit.sg.id for hit in hits.filter(key="fp")],
                }
       
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

            bindings = RouteSGBinding.objects.filter(route_id=route_id).select_related("sg")
            selected_sgs = [b.sg.id for b in bindings]

            print(f"Route {route_id}: Common true positives: {len(tp)}, common false positives: {len(fp)}, common false negatives: {len(fn)}, selected SGs: {len(selected_sgs)}")


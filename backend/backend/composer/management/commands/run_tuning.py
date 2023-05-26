from multiprocessing import Process
from time import perf_counter
import random

import optuna
from composer.models import Route, RouteLSABinding
from django.core.management.base import BaseCommand
from routing.matching import get_matches
from routing.matching.hypermodel import *


def calc_precision(tp, fp, fn):
    return tp / (tp + fp) if tp + fp > 0 else 0


def calc_recall(tp, fp, fn):
    return tp / (tp + fn) if tp + fn > 0 else 0


def calc_f1(tp, fp, fn):
    precision = calc_precision(tp, fp, fn)
    recall = calc_recall(tp, fn, fn)
    return 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0


METRICS = {
    "precision": calc_precision,
    "recall": calc_recall,
    "f1": calc_f1,
}

DIRECTIONS = {
    "precision": "maximize",
    "recall": "maximize",
    "f1": "maximize",
}

SELECTED_METRICS = ["f1"]


class Command(BaseCommand):
    help = """Use hyperparameter tuning to find the best matching configuration."""

    def search_best_configuration(self, hypermodel_cls, name: str):
        storage = f"sqlite:///config/{name}.optuna.db"
        if len(SELECTED_METRICS) == 1:
            study = optuna.create_study(
                study_name=name,
                direction=DIRECTIONS[SELECTED_METRICS[0]],
                storage=storage,
                load_if_exists=True,
                # pruner=optuna.pruners.HyperbandPruner(),
                sampler=optuna.samplers.TPESampler(),
            )
        else:
            study = optuna.create_study(
                study_name=name,
                directions=[DIRECTIONS[metric] for metric in SELECTED_METRICS],
                storage=storage,
                load_if_exists=True,
                sampler=optuna.samplers.TPESampler(),
            )

        def objective(trial):
            try:
                if study.best_trials:
                    best_trial = study.best_trials[0]
                    config = {
                        "params": best_trial.params,
                    }
                    for metric_idx, metric_name in enumerate(SELECTED_METRICS):
                        config[metric_name] = best_trial.values[metric_idx]
                    hypermodel_cls.store_config(config)
            except ValueError:
                pass

            trial_config = hypermodel_cls.get_trial_config(trial)
            matcher = hypermodel_cls(trial_config)

            routes_with_bindings = list(Route.objects \
                .filter(bound_lsas__isnull=False) \
                .distinct())
                
            random.shuffle(routes_with_bindings)

            def make_batch_generator(n_routes_per_batch):
                batch_idx = 0
                n_routes = len(routes_with_bindings)
                while True:
                    batch_start = batch_idx * n_routes_per_batch
                    batch_end = batch_start + n_routes_per_batch
                    if batch_end > n_routes:
                        batch_end = n_routes
                    if batch_start >= batch_end:
                        break
                    batch_idx += 1
                    yield routes_with_bindings[batch_start:batch_end]

            total_tp, total_fp, total_fn = 0, 0, 0
            total_duration = 0

            n_routes_per_batch = 10
            for batch_idx, batch in enumerate(make_batch_generator(n_routes_per_batch)):
                print(f"Study {name} processing batch {batch_idx}...")
                batch_tp, batch_fp, batch_fn = 0, 0, 0
                batch_duration = 0

                for step, route in enumerate(batch):
                    bindings = RouteLSABinding.objects \
                        .filter(route=route) \
                        .select_related("lsa")

                    selected_lsas = [b.lsa.id for b in bindings]

                    # Get the matched lsas
                    start = perf_counter()
                    matched_lsas = get_matches(route.geometry, [matcher])
                    end = perf_counter()
                    matched_lsas = [lsa.id for lsa in matched_lsas]

                    batch_tp += len(set(matched_lsas) & set(selected_lsas))
                    batch_fp += len(set(matched_lsas) - set(selected_lsas))
                    batch_fn += len(set(selected_lsas) - set(matched_lsas))
                    batch_duration += end - start

                # Only prune trials on full batches and when it's supported
                # (i.e. when we select for only one metric)
                if len(SELECTED_METRICS) == 1 and len(batch) == n_routes_per_batch:
                    metric_name = SELECTED_METRICS[0]
                    metric = METRICS[metric_name]
                    trial.report(metric(batch_tp, batch_fp, batch_fn), batch_idx)

                    if trial.should_prune():
                        raise optuna.TrialPruned()

                total_tp += batch_tp
                total_fp += batch_fp
                total_fn += batch_fn
                total_duration += batch_duration

            duration_per_route = total_duration / len(routes_with_bindings)
            print(f"Study {name} finished processing batches - TP: {total_tp}, FP: {total_fp}, FN: {total_fn}, Duration per Route: {duration_per_route}")
            results = []
            for metric in SELECTED_METRICS:
                total_metric = METRICS[metric](total_tp, total_fp, total_fn)
                results.append(total_metric)
            return results

        study.optimize(objective, timeout=60 * 600) # 10 hours

    def handle(self, *args, **options):
        print("Tuning the matching algorithms...")

        """ strategies = {
            "shortest-path": ShortestPathHypermodelMatcher,
            "strict-shortest-path": StrictShortestPathHypermodelMatcher,
            "probabilistic": ProbabilisticHypermodelMatcher,
        } """
        
        strategies = {
            "topological": TopologicHypermodelMatcher,
        }

        processes = []
        for strategy, hypermodel_cls in strategies.items():
            print(f"Tuning {strategy}...")
            p = Process(target=self.search_best_configuration, args=(hypermodel_cls, strategy))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()





import json
import os
from typing import List, Tuple

from django.conf import settings
from django.contrib.gis.geos.linestring import LineString
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.matching.bearing import BearingMatcher
from routing.matching.dijkstra import DijkstraMatcher, StrictDijkstraMatcher
from routing.matching.length import LengthMatcher
from routing.matching.markov import MarkovMatcher
from routing.matching.overlap import OverlapMatcher
from routing.matching.proximity import ProximityMatcher


class HypermodelMatcher(RouteMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/hypermodel.json')

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.matchers = self.__class__.get_sequential_model(config)

    @classmethod
    def load_config(cls) -> dict:
        try:
            with open(os.path.join(settings.BASE_DIR, cls.conf_file_path)) as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "params": {},
                "f1": 0,
            }

    @classmethod
    def store_config(cls, config: dict):
        """
        Store the configuration in the config file.

        The key "params" must be provided within the config, providing
        the hypermodel parameters.
        """
        assert "params" in config
        with open(os.path.join(settings.BASE_DIR, cls.conf_file_path), 'w') as f:
            json.dump(config, f, indent=2)

    @classmethod
    def from_config_file(cls, config_path=None) -> 'HypermodelMatcher':
        if config_path:
            try:
                with open(os.path.join(settings.BASE_DIR, config_path)) as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = cls.load_config()
        else:
            config = cls.load_config()
        params = config["params"]
        return cls(params)

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        raise NotImplementedError()

    @classmethod
    def get_sequential_model(cls, config) -> List[RouteMatcher]:
        raise NotImplementedError()

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        lsas, route = super().matches(lsas, route)
        for m in self.matchers:
            lsas, route = m.matches(lsas, route)
        return lsas, route


def get_best_hypermodel(key="f1"):
    configs = [subcls.load_config() for subcls in HypermodelMatcher.__subclasses__()]
    best_matcher_idx = max(range(len(configs)), key=lambda i: configs[i][key])
    best_matcher_conf = configs[best_matcher_idx]
    best_matcher_params = best_matcher_conf["params"]
    return HypermodelMatcher.__subclasses__()[best_matcher_idx](best_matcher_params)


class ProximityHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/proximity.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ ProximityMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { "search_radius_m": trial.suggest_int("search_radius_m", 1, 100) }


class BearingHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/bearing.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ BearingMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "bearing_threshold": trial.suggest_float("bearing_threshold", 0, 1),
            "bearing_diff_threshold": trial.suggest_float("bearing_diff_threshold", 0, 180),
            "match_inverted_bearings": trial.suggest_categorical("match_inverted_bearings", [True, False]),
        }


class LengthHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/length.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ LengthMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "length_threshold": trial.suggest_float("length_threshold", 0, 1),
            "length_diff_threshold": trial.suggest_float("length_diff_threshold", 0, 1),
        }


class OverlapHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/overlap.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ OverlapMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "road_side_threshold": trial.suggest_float("road_side_threshold", 0, 100),
            "perfect_match_threshold": trial.suggest_float("perfect_match_threshold", 0, 50),
            "overlap_pct_threshold": trial.suggest_float("overlap_pct_threshold", 0, 1),
        }


class MarkovHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/markov.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ MarkovMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "crossing_padding": trial.suggest_int("crossing_padding", 1, 50),
            "sigma_z": trial.suggest_float("sigma_z", 1, 10),
            "beta": trial.suggest_float("beta", 1, 10),
        }


class DijkstraHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/dijkstra.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ DijkstraMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "crossing_padding": trial.suggest_int("crossing_padding", 1, 50),
            "offlsa_penalty": trial.suggest_float("offlsa_penalty", 1, 10),
        }


class StrictDijkstraHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/strict-dijkstra.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ StrictDijkstraMatcher(**config) ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            "crossing_padding": trial.suggest_int("crossing_padding", 1, 50),
            "offlsa_penalty": trial.suggest_float("offlsa_penalty", 1, 10),
        }


class ShortestPathHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/shortest-path.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ 
            *ProximityHypermodelMatcher.get_sequential_model(config),
            *DijkstraHypermodelMatcher.get_sequential_model(config),
        ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            **ProximityHypermodelMatcher.get_trial_config(trial),
            **DijkstraHypermodelMatcher.get_trial_config(trial),
        }


class StrictShortestPathHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/strict-shortest-path.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ 
            *ProximityHypermodelMatcher.get_sequential_model(config),
            *StrictDijkstraHypermodelMatcher.get_sequential_model(config),
        ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            **ProximityHypermodelMatcher.get_trial_config(trial),
            **StrictDijkstraHypermodelMatcher.get_trial_config(trial),
        }


class ProbabilisticHypermodelMatcher(HypermodelMatcher):
    conf_file_path = os.path.join(settings.BASE_DIR, 'config/probabilistic.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [ 
            *ProximityHypermodelMatcher.get_sequential_model(config),
            *MarkovHypermodelMatcher.get_sequential_model(config),
        ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return { 
            **ProximityHypermodelMatcher.get_trial_config(trial),
            **MarkovHypermodelMatcher.get_trial_config(trial),
        }


class TopologicHypermodelMatcher(HypermodelMatcher):
    """
    A matcher which uses multiple topologic matchers in sequential order.
    """

    conf_file_path = os.path.join(settings.BASE_DIR, 'config/topologic.hypermodel.json')

    @classmethod
    def get_sequential_model(cls, config):
        return [
            *ProximityHypermodelMatcher.get_sequential_model(config),
            *BearingHypermodelMatcher.get_sequential_model(config),
            *LengthHypermodelMatcher.get_sequential_model(config),
            *OverlapHypermodelMatcher.get_sequential_model(config),
        ]

    @classmethod
    def get_trial_config(cls, trial) -> dict:
        return {
            **ProximityHypermodelMatcher.get_trial_config(trial),
            **BearingHypermodelMatcher.get_trial_config(trial),
            **LengthHypermodelMatcher.get_trial_config(trial),
            **OverlapHypermodelMatcher.get_trial_config(trial),
        }

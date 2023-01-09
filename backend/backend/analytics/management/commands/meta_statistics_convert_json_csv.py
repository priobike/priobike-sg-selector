import csv
import os
import numpy as np
import json
from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd


class Command(BaseCommand):

    logs_path = "analytics/logs/"

    def add_arguments(self, parser):
        parser.add_argument('--1', nargs='+')
        parser.add_argument('--2', nargs='+')

    def handle(self, *args, **options):

        algorithm_names = [options['1'][0], options['2'][0]]

        algorithms_statistics = {}

        for algorithm_name in algorithm_names:
            with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}run_analysis_constellation_route_errors/constellation_route_error_logs_{algorithm_name}.json")) as handle:
                algorithms_statistics[algorithm_name] = json.loads(
                    handle.read())

        # Create header
        csv_header = ['metaValue']
        for algorithm_name in algorithm_names:
            if algorithm_name == "algo-topo-pm-ts":
                csv_header.append("Algo.")
                csv_header.append("Algo.Ratio")
            else:
                csv_header.append("ML")
                csv_header.append("ML.Ratio")

        constellation_names = []
        route_error_names = []

        # Gather all constellation names
        for constellation in algorithms_statistics[algorithm_names[0]]["constellations_right_ratio"]:
            constellation_names.append(f"K-{constellation}")

        # Gather all route_error names
        for route_error in algorithms_statistics[algorithm_names[0]]["route_errors_right_ratio"]:
            route_error_names.append(
                f"R-{route_error}" if route_error != "Kein Fehler" else "Kein-Fehler")

        constellation_names.sort()
        route_error_names.sort()

        csv_rows = []

        # Add constellation statistics
        for constellation_name in constellation_names:
            csv_row = []
            csv_row.append(constellation_name)
            csv_row.append(algorithms_statistics[algorithm_names[0]]
                           ["constellations_right"][constellation_name.replace("K-", "")])
            ratio = algorithms_statistics[algorithm_names[0]
                                          ]["constellations_right_ratio"][constellation_name.replace("K-", "")]
            csv_row.append(f"{str(round(ratio * 100, 2))}\%")
            csv_row.append(algorithms_statistics[algorithm_names[1]]
                           ["constellations_right"][constellation_name.replace("K-", "")])
            ratio = algorithms_statistics[algorithm_names[1]
                                          ]["constellations_right_ratio"][constellation_name.replace("K-", "")]
            csv_row.append(f"{str(round(ratio * 100, 2))}\%")
            csv_rows.append(csv_row)

        # Add route_error statistics
        for route_error_name in route_error_names:
            csv_row = []
            csv_row.append(route_error_name)
            csv_row.append(algorithms_statistics[algorithm_names[0]]["route_errors_right"][route_error_name.replace(
                "R-", "").replace("-", " ")])
            ratio = algorithms_statistics[algorithm_names[0]]["route_errors_right_ratio"][route_error_name.replace(
                "R-", "").replace("-", " ")]
            csv_row.append(f"{str(round(ratio * 100, 2))}\%")
            csv_row.append(algorithms_statistics[algorithm_names[1]]["route_errors_right"][route_error_name.replace(
                "R-", "").replace("-", " ")])
            ratio = algorithms_statistics[algorithm_names[1]]["route_errors_right_ratio"][route_error_name.replace(
                "R-", "").replace("-", " ")]
            csv_row.append(f"{str(round(ratio * 100, 2))}\%")
            csv_rows.append(csv_row)

        algorithm_names_string = ""
        for algorithm_name in algorithm_names:
            algorithm_names_string = algorithm_names_string + \
                f"_{algorithm_name}"

        csv_file_path = os.path.join(
            settings.BASE_DIR, f"{self.logs_path}run_analysis_constellation_route_errors/_combined_absolute_statistics{algorithm_names_string}.csv")
        with open(csv_file_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow(csv_header)
            writer.writerows(csv_rows)

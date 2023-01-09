import json

from django.core.serializers import serialize
from django.db.models import Case, Count, FloatField, Q, When
from django.db.models.expressions import F
from django.db.models.functions import Cast
from django.http.response import Http404, JsonResponse
from django.views.generic import View
from routing.models import LSA

from analytics.models import Run


def cross_origin(response):
    response["Access-Control-Allow-Origin"] = "*"
    return response


class StatisticsResource(View):
    def get(self, request):
        algorithm_name = request.GET.get("algorithm_name")
        if not algorithm_name:
            # Get the most recent run
            run = Run.objects.order_by("-timestamp").first()
            if not run:
                print("No run found.")
                raise Http404
        else:
            # Get the most recent run with the given algorithm name
            run = Run.objects \
                .filter(algorithm_name=algorithm_name) \
                .order_by("-timestamp") \
                .first()
            if not run:
                print("No run found with algorithm name:", algorithm_name)
                raise Http404

        lsas = LSA.objects.filter(hits__isnull=False, hits__run=run)

        metrics = {
            "tp": Cast(Count("hits", filter=Q(hits__key="tp")), FloatField()),
            "fp": Cast(Count("hits", filter=Q(hits__key="fp")), FloatField()),
            "fn": Cast(Count("hits", filter=Q(hits__key="fn")), FloatField()),
            "tp_c": Cast(Count("hits", filter=Q(hits__key="tp_c")), FloatField()),
            "fp_c": Cast(Count("hits", filter=Q(hits__key="fp_c")), FloatField()),
            "fn_c": Cast(Count("hits", filter=Q(hits__key="fn_c")), FloatField()),
            "precision": Case(
                When(tp=0, then=0),
                default=F("tp") / (F("tp") + F("fp")),
                output_field=FloatField(),
            ),
            "precision_c": Case(
                When(tp_c=0, then=0),
                default=F("tp_c") / (F("tp_c") + F("fp_c")),
                output_field=FloatField(),
            ),
            "recall": Case(
                When(tp=0, then=0),
                default=F("tp") / (F("tp") + F("fn")),
                output_field=FloatField(),
            ),
            "recall_c": Case(
                When(tp_c=0, then=0),
                default=F("tp_c") / (F("tp_c") + F("fn_c")),
                output_field=FloatField(),
            ),
            "f1": Case(
                When(tp=0, then=0),
                default=2 * F("precision") * F("recall") / (F("precision") + F("recall")),
                output_field=FloatField(),
            ),
            "f1_c": Case(
                When(tp_c=0, then=0),
                default=2 * F("precision_c") * F("recall_c") / (F("precision_c") + F("recall_c")),
                output_field=FloatField(),
            ),
        }

        lsas = lsas.annotate(**metrics)

        geojson = serialize("geojson", list(lsas), geometry_field="geometry")
        geojson_data = json.loads(geojson)

        # Expand the properties dict with the computed fields
        values = iter(lsas.values(*metrics.keys()))
        for feature in geojson_data["features"]:
            feature["properties"].update(next(values))
            feature["properties"]["lsa"] = feature["properties"]["pk"]

        return cross_origin(JsonResponse(geojson_data))

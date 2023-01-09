from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


class StatusView(View):
    """
    View to get the status of the signal group selector.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle the GET request.
        """
        return JsonResponse({'status': 'ok'})


@method_decorator(csrf_exempt, name='dispatch')
class HealthcheckView(View):
    """
    View to get the healthcheck of the signal group selector.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle the GET request.
        """
        token = settings.HEALTHCHECK_TOKEN
        if token and token != request.GET.get('token'):
            return JsonResponse({'status': 'unauthorized'}, status=401)
        
        # Fetch all objects from all models.
        # This will heat the cache and make sure 
        # the database is available.
        now = datetime.now()
        for model in apps.get_models():
            model.objects.all()
        time = (datetime.now() - now).total_seconds()
        print(f'OK: Healthcheck took {time} seconds')
        
        return JsonResponse({'status': 'ok', 'time': time})

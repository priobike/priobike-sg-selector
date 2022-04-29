from django.http import JsonResponse
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

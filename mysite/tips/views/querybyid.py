import json

from django.contrib.messages import debug
from django.views import View
from django.db import connection
from django.http import JsonResponse, HttpResponse

from tips.views.views import logger


class QueryById(View):
    @staticmethod
    def post(request):
        if request.headers.get('Content-Type') != 'application/json':
            return HttpResponse('Request header error!', status=400)
        data = json.loads(request.body)
        tips_id = data.get('id')
        with connection.cursor() as cursor:
            query = "SELECT tips_id, species, description, display FROM data_info WHERE tips_id = %s"
            cursor.execute(query, (tips_id,))
            result = cursor.fetchone()

        if not result or not result[3]:
            return JsonResponse({'error': 'Tips ID not found.'}, status=404)
        response_data = {
            'pid': result[0],
            'species': result[1],
            'description': result[2]
        }
        return JsonResponse(response_data)


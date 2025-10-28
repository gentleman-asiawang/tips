from tips.models import DataInfo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def query_by_id(request):
    """
    根据 tips_id 查询数据，GET 请求
    请求参数：
        /tips_api/query_by_id/?id=123
    """
    tips_id = request.query_params.get('id')  # GET 参数
    if not tips_id:
        return Response({'error': 'Missing id parameter.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = DataInfo.objects.get(tips_id=tips_id)
    except DataInfo.DoesNotExist:
        return Response({'error': 'Tips ID not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not obj.display:  # display 字段为空
        return Response({'error': 'Tips ID not found.'}, status=status.HTTP_404_NOT_FOUND)

    response_data = {
        'pid': obj.tips_id,
        'species': obj.species,
        'description': obj.description
    }
    return Response(response_data)

from tips.models import DataInfo, FileInfo
from tips.views.my_module import UuidManager

import tempfile
import psutil
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
import time
import os
logger = logging.getLogger(__name__)

# Create your views here.
@api_view(['POST'])
def login(request):
    uuid = request.data.get('uuid')
    if not uuid:
        return Response({'error': 'uuid missing'}, status=status.HTTP_400_BAD_REQUEST)
    UuidManager.add_entry(uuid, 'uuid', uuid)
    # 创建uuid目录
    uuid_path = os.path.join(settings.TEMP_DIR, uuid)
    try:
        os.makedirs(uuid_path, exist_ok=True)
    except Exception as e:
        return Response({'error': f'Failed to create dir: {e}'}, status=status.HTTP_403_FORBIDDEN)
    return Response({'message': 'Successfully connect!'})

@api_view(['POST'])
def get_orders(request):
    try:
        # 查询所有 orders 并去重
        orders_list = list(DataInfo.objects.values_list('orders', flat=True).distinct())

        # 总条目数
        count_all = DataInfo.objects.count()

        # 不同物种数
        count_species = DataInfo.objects.values('species').distinct().count()

        return Response({
            'status': 'success',
            'orders': orders_list,
            'picture_url': 'https://tips.shenxlab.com/media/',
            'count_all': count_all,
            'count_species': count_species,
            'data_size': 3172
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReceiveFileAPIView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file_type = request.headers.get('File-Type')
        uuid = request.headers.get('uuid')

        if not uuid:
            return Response({'error': 'UUID missing in headers'}, status=status.HTTP_400_BAD_REQUEST)

        if file_type not in ['pdb', 'fasta']:
            return Response({'error': 'File type not supported!'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存文件并记录
        if file_type == 'fasta':
            logger.debug("Detect fasta file and save it temporarily to local")
        else:
            logger.debug("Detect pdb file and save it temporarily to local")

        file_path = self.save_temp_file(uploaded_file, uuid, file_type)
        UuidManager.add_entry(uuid, file_type, file_path)

        return Response({'message': 'Successfully received file!'}, status=status.HTTP_200_OK)

    @staticmethod
    def save_temp_file(uploaded_file, uuid, file_type='pdb'):
        suffix = f'.{file_type}' if file_type in ['pdb', 'fasta'] else ''
        temp_dir = str(os.path.join(settings.TEMP_DIR, uuid))
        os.makedirs(temp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=suffix) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            return temp_file.name


@api_view(['POST'])
def delete_all_temp_files(request):
    uuid = request.data.get('uuid')  # DRF 自动解析 POST 数据
    if not uuid:
        return Response({'error': 'UUID missing'}, status=status.HTTP_400_BAD_REQUEST)

    # 删除文件和 uuid 对应条目
    UuidManager.delete_uuid_entry(uuid)
    logger.debug(f"The files under {uuid} have been completely deleted")

    # 返回 204 No Content
    return Response(status=status.HTTP_204_NO_CONTENT)

class GetServerLoadAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # 验证 uuid
        uuid = request.headers.get('uuid')
        if uuid not in UuidManager.uuid_storage:
            return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serverload = self.get_load()
        return Response({'serverload': serverload})

    @staticmethod
    def get_load():
        # 初次采样
        io_counters_start = psutil.disk_io_counters()
        start_time = time.time()
        cpu_load = psutil.cpu_percent(0.5)
        # 等待一个短时间间隔以便计算速率
        # 第二次采样
        io_counters_end = psutil.disk_io_counters()
        end_time = time.time()
        # 计算时间差
        time_diff = end_time - start_time
        # 计算读取占用率（以 MB/s 为单位）
        read_bytes = io_counters_end.read_bytes - io_counters_start.read_bytes
        read_speed_mb_s = read_bytes / time_diff / (1024 * 1024)
        logger.debug(f'cpu:{cpu_load};io:{read_speed_mb_s}')
        if cpu_load >= 80 or read_speed_mb_s >= 800:
            return "high"
        elif 20 < cpu_load < 80 or 100 < read_speed_mb_s < 800:
            return "medium"
        else:
            return "low"

@api_view(['GET'])
def get_file_info(request):
    uuid = request.headers.get('uuid')
    if uuid not in UuidManager.uuid_storage:
        return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)
    with connection.cursor() as cursor:
        # 查询所有目
        file_info_list = list(FileInfo.objects.values())
    return JsonResponse(file_info_list, safe=False, status=200)

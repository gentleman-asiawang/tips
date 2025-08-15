from django.http import HttpResponse
from tips.views.my_module import UuidManager
from django.views import View
import tempfile
import psutil
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
import logging
import time
import os
logger = logging.getLogger(__name__)

# Create your views here.
class GetUuid(View):
    @staticmethod
    def post(request):
        uuid = request.POST.get('uuid')
        UuidManager.add_entry(uuid, 'uuid', uuid)
        # 创建uuid目录
        uuid_path = f'{settings.TEMP_DIR}/{uuid}'
        try:
            os.makedirs(uuid_path, exist_ok=True)
        except Exception as e:
            return HttpResponse(f'fail to create dir {e}', status=403)
        return HttpResponse('successfully connect!')

class GetOrders(View):
    @staticmethod
    def post(request):
        with connection.cursor() as cursor:
            # 查询所有目
            cursor.execute("SELECT DISTINCT orders FROM data_info")
            orders = cursor.fetchall()
            cursor.execute("SELECT COUNT(tips_id) FROM data_info")
            count_all = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT species) FROM data_info")
            count_species = cursor.fetchone()[0]

        orders_list = [order[0] for order in orders]
        # 返回JSON响应
        return JsonResponse({'status': 'success', 'orders': orders_list, 'picture_url': 'https://tips.shenxlab.com/media/',
                             'count_all': count_all, 'count_species': count_species, 'data_size': 3172})


class ReceiveFile(View):
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_type = request.headers.get('File-Type')
            uuid = request.headers.get('uuid')
            if file_type in ['pdb', 'fasta']:
                if file_type == 'fasta': # 暂时用不上，但是以后可能会用上，所以保留
                    logger.debug(f"Detect fasta file and save it temporarily to local")
                    UuidManager.add_entry(uuid, file_type, self.save_temp_file(uploaded_file, uuid))
                else:
                    logger.debug(f"Detect pdb file and save it temporarily to local")
                    UuidManager.add_entry(uuid, file_type, self.save_temp_file(uploaded_file, uuid))

                return HttpResponse('successfully receive file!')
            else:
                return HttpResponse('file type not supported!', status=400)
        return None

    @staticmethod
    def save_temp_file(uploaded_file, uuid):
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.pdb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            return temp_file.name

class DeleteAllTempFiles(View):
    @staticmethod
    def post(request):
        uuid = request.POST.get('uuid')
        # 删除文件和uuid对应的条目
        UuidManager.delete_uuid_entry(uuid)
        logger.debug(f"The files under {uuid} have been completely deleted")
        return HttpResponse(status=204)

class GetServerLoad(View):
    def post(self, request):
        uuid = request.headers.get('uuid')
        if uuid not in UuidManager.uuid_storage:
            return JsonResponse({'error': 'uuid does not exist'}, status=404)
        return  JsonResponse({'serverload': self.get_load()})

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
        elif 20 < cpu_load < 0.8 or 100 < read_speed_mb_s < 800:
            return "medium"
        else:
            return "low"

class GetFileinfo(View):
    @staticmethod
    def get(request):
        uuid = request.headers.get('uuid')
        if uuid not in UuidManager.uuid_storage:
            return JsonResponse({'error': 'uuid does not exist'}, status=404)
        with connection.cursor() as cursor:
            # 查询所有目
            cursor.execute("SELECT * FROM file_info")
            file_info_query = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            # 将结果转换为字典列表
            file_info_list = [
                dict(zip(column_names, row)) for row in file_info_query
            ]
        return JsonResponse(file_info_list, safe=False, status=200)

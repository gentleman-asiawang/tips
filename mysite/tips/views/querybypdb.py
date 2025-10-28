import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.views.my_module import UuidManager, FileReshape, logger
import os, subprocess, logging
logger = logging.getLogger(__name__)


class QueryByPDB(APIView):
    """
    根据 PDB 文件和 foldseek_db 查询 Foldseek 结果
    POST JSON body:
    {
        "foldseek_db": "All" 或其他库名,
        "sample": true 或 false
    }
    Headers:
        uuid: 用户 UUID
    """
    def post(self, request):
        uuid = request.headers.get('uuid')
        if not uuid:
            return Response({'error': 'uuid parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if uuid not in UuidManager.uuid_storage:
            return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)
        # 获取 POST 数据
        data = request.data
        foldseek_db = data.get('foldseek_db')
        sample = data.get('sample', False)

        temp_pdb_path = UuidManager.get_files_for_uuid(uuid).get('pdb')
        if not sample:
            if not os.path.exists(temp_pdb_path):
                return JsonResponse({'error': 'PDB file not found'}, status=status.HTTP_404_NOT_FOUND)

        if foldseek_db == "All":
            foldseek_db_path = f'/tips_db/foldseek_db/All_70pLDDT_db/all_70pLDDT'
        else:
            foldseek_db_path = f'/tips_db/foldseek_db/{foldseek_db}_db/{foldseek_db}'


        if sample:
            temp_pdb_path = os.path.join(settings.BASE_DIR, 'tips', 'data', '6RKF_A.pdb')
            out_file_path = f'{settings.TEMP_DIR}/{uuid}/6RKF_A_pdb_{foldseek_db}_result.tsv'
        else:
            out_file_path = f'{settings.TEMP_DIR}/{uuid}/{os.path.splitext(os.path.basename(temp_pdb_path))[0]}_pdb_{foldseek_db}_result.tsv'

        UuidManager.add_entry(uuid, 'foldseek_tsv', out_file_path)
        tmp_path = '/tips_db/foldseek_db/tmp'
        foldseek_command = ['foldseek', 'easy-search', '--threads', '16', temp_pdb_path, foldseek_db_path,
                            out_file_path, tmp_path, '-s', '9.5', '--max-seqs', '1000', '-e', '0.001',
                            '--prefilter-mode', '1',
                            '--alignment-type', '2', '--cov-mode', '0', '--format-mode', '4', '--format-output',
                            'target,fident,evalue,bits,prob,lddt,qstart,qend,tstart,tend,tlen,qcov,tcov,alntmscore']
        try:
            subprocess.run(foldseek_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr
            return Response({'error': 'Foldseek command failed', 'details': error_output}, status=status.HTTP_400_BAD_REQUEST)

        foldseek_data = FileReshape.read_tsv_file(tsv_file_path=out_file_path, out_type="foldseek", uuid=uuid)
        return Response(foldseek_data)


# foldseek easy-search query.pdb(查询的文件) class_DB(数据库位置) aln.m8(输出结果) tmpFolder(需指定临时文件夹)

# foldseek easy-search --threads 16 ./Diptera_Acrocera_orbiculus_at_ENSCRRG00000011446.1.pdb
# /data/tips_db/foldseek_db/Diptera_db/ ./out_all.tsv ./tmp -s 9.5 --max-seqs 1000 -e 10 --alignment-type 2
# --cov-mode 0 --format-mode 4 --format-output 'query,target,alntmscore,fident,evalue,bits,prob,lddt,qstart,qend,
# tstart,tend,qcov,tcov'
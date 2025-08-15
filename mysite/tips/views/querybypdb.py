import os
import json
import subprocess
from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from tips.views.my_module import UuidManager, FileReshape, logger


class QueryByPDB(View):
    @staticmethod
    def post(request):
        if request.headers.get('Content-Type') != 'application/json':
            return JsonResponse({'error': 'Request header error!'}, status=400)
        uuid = request.headers.get('uuid')
        data = json.loads(request.body)
        foldseek_db = data.get('foldseek_db')
        sample = data.get('sample')
        logger.debug(sample)
        temp_pdb_path = UuidManager.get_files_for_uuid(uuid).get('pdb')
        if not sample:
            if not os.path.exists(temp_pdb_path):
                return JsonResponse({'error': 'PDB file not found'}, status=400)

        if foldseek_db == "All":
            foldseek_db_path = f'/tips_db/foldseek_db/All_70pLDDT_db/all_70pLDDT'
        else:
            foldseek_db_path = f'/tips_db/foldseek_db/{foldseek_db}_db/{foldseek_db}'


        if sample:
            temp_pdb_path = "/data/Data/Example/6RKF_A.pdb"
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
            result = subprocess.run(foldseek_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr
            return JsonResponse({'error': 'Foldseek command failed', 'details': error_output}, status=400)
        if not result.returncode == 0:
            return HttpResponse('foldseek command failed!')
        foldseek_data = FileReshape.read_tsv_file(tsv_file_path=out_file_path, out_type="foldseek", uuid=uuid)
        return JsonResponse(foldseek_data, safe=False)


# foldseek easy-search query.pdb(查询的文件) class_DB(数据库位置) aln.m8(输出结果) tmpFolder(需指定临时文件夹)

# foldseek easy-search --threads 16 ./Diptera_Acrocera_orbiculus_at_ENSCRRG00000011446.1.pdb
# /data/tips_db/foldseek_db/Diptera_db/ ./out_all.tsv ./tmp -s 9.5 --max-seqs 1000 -e 10 --alignment-type 2
# --cov-mode 0 --format-mode 4 --format-output 'query,target,alntmscore,fident,evalue,bits,prob,lddt,qstart,qend,
# tstart,tend,qcov,tcov'
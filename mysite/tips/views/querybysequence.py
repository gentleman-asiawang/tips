import os
import json
import logging
import tempfile
import subprocess
import time

from django.views import View
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from tips.views.my_module import UuidManager, FileReshape
logger = logging.getLogger(__name__)



class QueryBySequence(View):
    @staticmethod
    def post(request):
        if request.headers.get('Content-Type') != 'application/json':
            return JsonResponse({'error': 'Request header error!'}, status=400)
        time.sleep(0.3)
        uuid = request.headers.get('uuid')
        data = json.loads(request.body)
        mmseqs_db = data.get('mmseqs_db')
        if mmseqs_db == "All":
            # mmseqs_db_path = f'/tips_db/mmseqs_db/All_db/all'
            mmseqs_db_path = f'/tips_db/mmseqs_db/All_70pLDDT_db/all_70pLDDT'
        else:
            mmseqs_db_path = f'/tips_db/mmseqs_db/{mmseqs_db}_db/{mmseqs_db}'

        sequence = data.get('sequence')
        if not sequence:
            return JsonResponse({'error': 'No sequence provided'}, status=400)
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.faa') as temp_seq_file:
            if not sequence.startswith(">"):
                temp_seq_file.write(f'>query_sequence\n{sequence}\n'.encode('utf-8'))
            else:
                lines = sequence.splitlines()
                if len(lines) < 2:
                    return JsonResponse({'error': 'Please check your input data!'}, status=400)
                temp_seq_file.write(f'{sequence}\n'.encode('utf-8'))
            temp_seq_path = temp_seq_file.name
            logger.debug(f"Temp_seq_path: {temp_seq_path}")
            UuidManager.add_entry(uuid, 'fasta', temp_seq_path)

        out_file_path = f'{settings.TEMP_DIR}/{uuid}/{os.path.splitext(os.path.basename(temp_seq_path))[0]}_faa_{mmseqs_db}_result.tsv'
        UuidManager.add_entry(uuid, 'mmseq2_tsv', out_file_path)

        mmseq_command = ['mmseqs', 'easy-search', '--threads', '16', temp_seq_path, mmseqs_db_path, out_file_path,
                         '/tips_db/mmseqs_db/tmp', '--max-seqs', '1000', '-s', '9.5', '--prefilter-mode', '1',
                         '-e', '0.001', '--cov-mode', '0', '--format-mode', '4', '--format-output',
                         'target,fident,evalue,bits,pident,qstart,qend,tstart,tend,tlen,qcov,tcov']
        try:
            result = subprocess.run(mmseq_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr
            return JsonResponse({'error': 'Command failed', 'details': error_output}, status=400)
        logger.debug(f"Mmseqs search done!")
        if not result.returncode == 0:
            return HttpResponse('command failed!')
        mmseqs_data = FileReshape.read_tsv_file(tsv_file_path=out_file_path, out_type="mmseqs", uuid=uuid)
        return JsonResponse(mmseqs_data, safe=False)
import os
import json
import logging
import tempfile
import subprocess
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from tips.views.my_module import UuidManager, FileReshape

logger = logging.getLogger(__name__)


@api_view(['POST'])
def query_by_sequence(request):
    uuid = request.headers.get('uuid')
    if uuid not in UuidManager.uuid_storage:
        return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)
    data = json.loads(request.body)
    mmseqs_db = data.get('mmseqs_db')
    sequence = data.get('sequence')

    if not sequence:
        return Response({'error': 'No sequence provided'}, status=status.HTTP_400_BAD_REQUEST)

    if mmseqs_db == "All":
        # mmseqs_db_path = f'/tips_db/mmseqs_db/All_db/all'
        mmseqs_db_path = f'/tips_db/mmseqs_db/All_70pLDDT_db/all_70pLDDT'
    else:
        mmseqs_db_path = f'/tips_db/mmseqs_db/{mmseqs_db}_db/{mmseqs_db}'

    temp_dir = os.path.join(settings.TEMP_DIR, uuid)
    os.makedirs(temp_dir, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix='.faa') as temp_seq_file:
        if not sequence.startswith(">"):
            temp_seq_file.write(f'>query_sequence\n{sequence}\n'.encode('utf-8'))
        else:
            lines = sequence.splitlines()
            if len(lines) < 2:
                return Response({'error': 'Please check your input data!'}, status=status.HTTP_400_BAD_REQUEST)
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
        logger.error(f"Mmseqs command failed: {e.stderr}")
        return Response({'error': 'Command failed', 'details': e.stderr}, status=status.HTTP_400_BAD_REQUEST)

    if result.returncode != 0:
        return Response({'error': 'Command failed!'}, status=status.HTTP_400_BAD_REQUEST)
    mmseqs_data = FileReshape.read_tsv_file(tsv_file_path=out_file_path, out_type="mmseqs", uuid=uuid)
    logger.debug("Mmseqs search done!")

    return Response(mmseqs_data)
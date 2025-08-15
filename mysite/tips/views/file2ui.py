import os
import re
import json
import logging
import zipfile
import tempfile
import subprocess
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from django.views import View
from django.conf import settings
from django.db import connection
from tips.views.my_module import UuidManager
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Alignment, Border, Side
from django.http import FileResponse, JsonResponse, HttpResponse

logger = logging.getLogger(__name__)

class GetPDBFile(View):
    @staticmethod
    def get(request):
        tipsid = request.GET.get('tipsid')
        if not tipsid:
            return JsonResponse({'error': 'pdb_file_name parameter is required'}, status=400)
        with connection.cursor() as cursor:
            query = "SELECT basename FROM data_info WHERE tips_id = %s"
            cursor.execute(query, (tipsid,))
            pdb_file_name = cursor.fetchone()[0]
        logger.debug(pdb_file_name)
        match = re.match(r'^(.*?)_at_', pdb_file_name)
        if match:
            filename = match.group(1)
        else:
            return JsonResponse({'error': 'Invalid basename format'}, status=400)
        pdb_file_path = os.path.join('/data/Data/Structure', filename, pdb_file_name + ".pdb")  # 替换为实际路径
        if os.path.exists(pdb_file_path):
            modified_lines = []
            with open(pdb_file_path,'r') as file:
                for line in file:
                    if line.startswith("ATOM"):
                        columns = list(line)
                        original_value = float(line[61:66].strip())
                        if original_value < 1:
                            modified_value = original_value * 100
                            formatted_value = f"{modified_value:6.2f}"
                            columns[61:66] = formatted_value[:8]
                            modified_line = "".join(columns)
                            modified_lines.append(modified_line)
                        else:
                            modified_lines.append(line)
                    else:
                        modified_lines.append(line)



            return HttpResponse(modified_lines, content_type='chemical/x-pdb')

            #return FileResponse(open(pdb_file_path, 'rb'), content_type='chemical/x-pdb')
        else:
            return JsonResponse({'error': 'File not found'}, status=404)


class DownloadTable(View):
    @staticmethod
    def generate_excel_with_custom_dimensions(df):
        output = BytesIO()
        wb = Workbook()
        ws = wb.active

        # 设置标题样式
        header_font = Font(bold=True, color="000000")
        alignment = Alignment(horizontal="left")  # 设置左对齐
        thin_border = Border(
            left=Side(style=None),
            right=Side(style=None),
            top=Side(style=None),
            bottom=Side(style=None)
        )

        # 将 DataFrame 数据写入工作表
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            ws.append(row)
            for cell in ws[r_idx]:
                if r_idx == 1:  # 应用标题行样式
                    cell.font = header_font
                    cell.alignment = alignment
                    cell.border = thin_border  # 去除默认边框
                else:
                    # 设置数据行的样式
                    cell.border = thin_border

                cell.value = str(cell.value)

        # 设置列宽 (示例值，可以根据列名的宽度动态调整)
        for col in ws.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max_length + 2  # 设置宽度为最大值+2

        wb.save(output)
        output.seek(0)
        return output

    def post(self, request):
        if request.headers.get('Content-Type') != 'application/json':
            return JsonResponse({'error': 'Request header error!'}, status=400)
        uuid = request.headers.get('uuid')
        if not uuid:
            return JsonResponse({'error': 'uuid parameter is required'}, status=400)
        if uuid not in UuidManager.uuid_storage:
            return JsonResponse({'error': 'uuid does not exist'}, status=404)
        data = json.loads(request.body)
        download_type = data.get('download_type')
        if not download_type:
            return JsonResponse({'error': 'download type parameter is required'}, status=400)
        if download_type not in ['foldseek', 'mmseq2']:
            return JsonResponse({'error': 'download type error'}, status=400)
        download_type = f'reshape_{download_type}_tsv'
        outfile_path = UuidManager.get_files_for_uuid(uuid).get(download_type)


        df = pd.read_csv(outfile_path, sep='\t')  # 使用制表符作为分隔符

        output = self.generate_excel_with_custom_dimensions(df)

        if download_type == 'foldseek_tsv':
            outfile_name = 'foldseekoutput.tsv'
        else:
            outfile_name = 'mmseq2.tsv'
        logger.debug(f'Send {outfile_path} to ui')
        return FileResponse(output, as_attachment=True, filename=outfile_name)


class DownloadData(View):
    def post(self, request):
        if request.headers.get('Content-Type') != 'application/json':
            return HttpResponse('Request header error!', status=400)
        uuid = request.headers.get('uuid')
        data = json.loads(request.body)
        tips_id = data.get('tips_id')
        down_seq = data.get('sequence', False)
        if uuid is None:
            return JsonResponse({'error': 'uuid parameter is required'}, status=400)
        if uuid not in UuidManager.uuid_storage:
            return JsonResponse({'error': 'uuid does not exist'}, status=404)
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(tips_id))
            logger.debug(f'placeholders: {placeholders}')
            logger.debug(f'UUID: {uuid}')
            logger.debug(f'tips_id: {tips_id}')
            #query = f"SELECT basename FROM data_info WHERE tips_id = %s"
            query = f"SELECT basename FROM data_info WHERE tips_id IN ({placeholders})"
            cursor.execute(query, tips_id)
            full_file_paths = [self.get_full_path(row[0]) for row in cursor.fetchall()]
            logger.debug(f'full_file_paths:{full_file_paths}')
        if down_seq:
            seq_path = self.get_sequence(tips_id, uuid)
        else:
            seq_path = None

        if len(full_file_paths) == 1:
            outpath = full_file_paths[0]
        else:
            outpath = self.create_zip(full_file_paths, seq_path, uuid)
        return FileResponse(open(outpath, 'rb'), as_attachment=True, filename='files.zip')


    @staticmethod
    def create_zip(pdb_file_list, seq_path, uuid):
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.zip') as temp_zip_file:
            zip_file_path = temp_zip_file.name
            UuidManager.add_entry(uuid, 'zip', zip_file_path)
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                if seq_path:
                    zipf.write(seq_path, arcname=f'data/select.fasta')
                for filename in pdb_file_list:
                    logger.debug(filename)
                    zipf.write(filename, arcname=f'data/Structure/{os.path.basename(filename)}')
                return zip_file_path


    @staticmethod
    def get_full_path(basename):
        base_path = "/data/Data/Structure/"
        name_dir = re.match(r'^(.*?)_at_', basename).group(1)
        logger.debug(f'namedir: {name_dir}')
        return f'{base_path}{name_dir}/{basename}.pdb'


    @staticmethod
    def get_sequence(seq_list, uuid):
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.fasta') as temp_seq_file:
            temp_seq_file_path = temp_seq_file.name
            UuidManager.add_entry(uuid, 'fasta', temp_seq_file_path)
            list_input = ','.join(seq_list)
            blast_cmd = ['blastdbcmd', '-db', '/tips_db/blast_db/all_db/all', '-entry', list_input, '-dbtype', 'prot',
                         '-out', temp_seq_file_path]
        try:
            result = subprocess.run(blast_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr
            return JsonResponse({'error': 'Blast command failed', 'details': error_output}, status=400)
        if not result.returncode == 0:
            return HttpResponse('blast command failed!')
        return temp_seq_file_path
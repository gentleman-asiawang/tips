import os
import re
import zipfile
import tempfile
import subprocess
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from django.conf import settings
from tips.views.my_module import UuidManager
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Alignment, Border, Side
from django.http import FileResponse, HttpResponse
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tips.models import DataInfo
import logging

logger = logging.getLogger(__name__)


class GetPDBFile(APIView):
    """
       根据 tips_id 返回 PDB 文件，ATOM 列小于 1 的值放大 100 倍。
       GET 参数: tipsid
    """
    def get(self, request):
        uuid = request.headers.get('uuid')
        if not uuid:
            return Response({'error': 'uuid parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if uuid not in UuidManager.uuid_storage:
            return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)

        tips_id = request.data.get('tipsid')
        if not tips_id:
            return Response({'error': 'tipsid parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        pdb_file_name = DataInfo.objects.filter(tips_id=tips_id).values_list('basename', flat=True).first()
        if not pdb_file_name:
            return Response({'error': 'Tips ID not found.'}, status=status.HTTP_404_NOT_FOUND)

        match = re.match(r'^(.*?)_at_', pdb_file_name)
        if match:
            filename = match.group(1)
        else:
            return Response({'error': 'Invalid basename format'}, status=status.HTTP_400_BAD_REQUEST)
        pdb_file_path = os.path.join('/data/Data/Structure', filename, pdb_file_name + ".pdb")  # 替换为实际路径
        if not os.path.exists(pdb_file_path):
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        modified_lines = []

        with open(pdb_file_path,'r') as file:
            for line in file:
                if line.startswith("ATOM"):
                    columns = list(line)
                    try:
                        original_value = float(line[61:66].strip())
                    except ValueError:
                        modified_lines.append(line)
                        continue
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


class DownloadTable(APIView):
    """
    根据 uuid 和 download_type 生成 Excel 文件下载
    POST JSON body:
    {
        "download_type": "foldseek" 或 "mmseq2"
    }
    """
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
        uuid = request.headers.get('uuid')
        if uuid is None:
            return Response({'error': 'uuid parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if uuid not in UuidManager.uuid_storage:
            return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        download_type = data.get('download_type')
        if not download_type:
            return Response({'error': 'download type parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if download_type not in ['foldseek', 'mmseq2']:
            return Response({'error': 'download type error'}, status=status.HTTP_404_NOT_FOUND)
        download_type = f'reshape_{download_type}_tsv'
        outfile_path = UuidManager.get_files_for_uuid(uuid).get(download_type)
        if not outfile_path or not os.path.exists(outfile_path):
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        df = pd.read_csv(outfile_path, sep='\t')  # 使用制表符作为分隔符

        output = self.generate_excel_with_custom_dimensions(df)

        outfile_name = 'foldseek.xlsx' if download_type == 'foldseek' else 'mmseq2.xlsx'
        logger.debug(f'Send {outfile_path} to ui')
        return FileResponse(output, as_attachment=True, filename=outfile_name, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


class DownloadData(APIView):
    def post(self, request):
        uuid = request.headers.get('uuid')
        if uuid is None:
            return Response({'error': 'uuid parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if uuid not in UuidManager.uuid_storage:
            return Response({'error': 'uuid does not exist'}, status=status.HTTP_404_NOT_FOUND)


        data = request.data
        if not isinstance(data, dict):
            # 如果不是字典，则说明 JSON 无效
            raise ParseError('Invalid JSON body')
        tips_id = data.get('tips_id')
        down_seq = data.get('sequence', False)
        if not tips_id or not isinstance(tips_id, list):
            return Response({'error': 'tips_id must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)


        if not tips_id:
            return Response({'error': 'tips_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        data_infos = DataInfo.objects.filter(tips_id__in=tips_id)
        if not data_infos.exists():
            return Response({'error': 'No data found for given tips_id'}, status=status.HTTP_404_NOT_FOUND)

        full_file_paths = [self.get_full_path(di.basename) for di in data_infos]

        seq_path = None
        if down_seq:
            try:
                seq_path = self.get_sequence(tips_id, uuid)
            except subprocess.CalledProcessError as e:
                return Response({'error': 'Blast command failed', 'details': e.stderr},
                                status=status.HTTP_400_BAD_REQUEST)

        if len(full_file_paths) == 1 and not seq_path:
            outpath = full_file_paths[0]
        else:
            outpath = self.create_zip(full_file_paths, seq_path, uuid)
        return FileResponse(open(outpath, 'rb'), as_attachment=True, filename='files.zip')


    @staticmethod
    def create_zip(pdb_file_list, seq_path, uuid):
        temp_dir = f'{settings.TEMP_DIR}/{uuid}'
        os.makedirs(temp_dir, exist_ok=True)
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
        temp_dir = f'{settings.TEMP_DIR}/{uuid}'
        os.makedirs(temp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.fasta') as temp_seq_file:
            temp_seq_file_path = temp_seq_file.name
            UuidManager.add_entry(uuid, 'fasta', temp_seq_file_path)
            list_input = ','.join(seq_list)
            blast_cmd = ['blastdbcmd', '-db', '/tips_db/blast_db/all_db/all', '-entry', list_input, '-dbtype', 'prot',
                         '-out', temp_seq_file_path]
        subprocess.run(blast_cmd, capture_output=True, text=True, check=True)
        return temp_seq_file_path
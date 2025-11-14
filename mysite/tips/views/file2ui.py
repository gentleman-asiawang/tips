import os
import re
import io
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
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tips.models import DataInfo
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_pdb_file(request):
    """
    根据 tips_id 返回 PDB 文件，ATOM 列小于 1 的值放大 100 倍。
    GET 参数: tipsid
    """
    tips_id = request.query_params.get('tipsid')
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

        tips_id = request.data.get('tips_id')
        if not tips_id:
            return Response({'error': 'tips_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not tips_id or not isinstance(tips_id, list):
            return Response({'error': 'tips_id must be a non-empty list'}, status=status.HTTP_404_NOT_FOUND)

        # 三种情况，pdb、sequence、both
        down_type = request.data.get('down_type', 'pdb') # 默认只下载pdb
        if not down_type:
            return Response({'error': 'down_type parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        if down_type not in ['pdb', 'sequence', 'both']:
            return Response({'error': 'Download type error'}, status=status.HTTP_404_NOT_FOUND)

        data_infos = DataInfo.objects.filter(tips_id__in=tips_id)
        found_ids = set(data_infos.values_list('tips_id', flat=True))
        missing_ids = set(tips_id) - found_ids
        if missing_ids:
            return Response({'warning': 'Some tips_id not found', 'missing_ids': list(missing_ids)}, status=status.HTTP_404_NOT_FOUND)
        if found_ids is None:
            return Response({'error': 'No data found for given tips_id'}, status=status.HTTP_404_NOT_FOUND)

        fasta_text = None
        if down_type == 'both':
            try:
                fasta_text = self.get_sequence(tips_id)
            except subprocess.CalledProcessError as e:
                return Response({'error': 'Blast command failed', 'details': e.stderr},
                                status=status.HTTP_400_BAD_REQUEST)
        elif down_type == 'pdb': # 只输出结构的情况，如果只输出一个就不需要打包，否则需要打包返回
            full_file_paths = [self.get_full_path(di.basename) for di in data_infos]
            if len(full_file_paths) == 1: # 只输出一个，直接返回序列文件
                full_path = full_file_paths[0]
                ext = os.path.splitext(full_path)[1]
                filename = f"select{ext}"
                return FileResponse(open(full_file_paths[0], 'rb'), as_attachment=True, filename=filename)
            else: # 选择了多个文件，要打包后返回
                buffer = self.create_zip_in_memory(full_file_paths, fasta_text)
                return FileResponse(buffer, as_attachment=True, filename='select.zip')
        else: # 只输出序列的情况，不需要压缩，直接返回
            try:
                fasta_text = self.get_sequence(tips_id)
            except subprocess.CalledProcessError as e:
                return Response({'error': 'Blast command failed', 'details': e.stderr},
                                status=status.HTTP_400_BAD_REQUEST)
            if fasta_text is None:
                return Response({'error': 'Fasta file not found'}, status=status.HTTP_404_NOT_FOUND)
            fasta_bytes = BytesIO(fasta_text.encode("utf-8"))
            return FileResponse(fasta_bytes, as_attachment=True, filename='select.fasta')


    @staticmethod
    def create_zip(pdb_file_list, fasta_text, uuid):
        temp_dir = f'{settings.TEMP_DIR}/{uuid}'
        os.makedirs(temp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}', suffix='.zip') as temp_zip_file:
            zip_file_path = temp_zip_file.name
            UuidManager.add_entry(uuid, 'zip', zip_file_path)
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                if fasta_text is not None:
                    zipf.write(fasta_text, arcname=f'data/select.fasta')
                if len(pdb_file_list) == 1:
                    zipf.write(pdb_file_list[0], arcname=f'data/{os.path.basename(pdb_file_list[0])}')
                else:
                    for filename in pdb_file_list:
                        logger.debug(filename)
                        zipf.write(filename, arcname=f'data/Structure/{os.path.basename(filename)}')
            return zip_file_path

    @staticmethod
    def create_zip_in_memory(pdb_file_list, fasta_text):
        buffer = io.BytesIO()  # 内存中存放 ZIP

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 写入 FASTA（直接内存文本）
            if fasta_text:
                zipf.writestr("select.fasta", fasta_text)

            # 写入 pdb 文件（读取本地文件内容到内存 ZIP）
            if len(pdb_file_list) == 1:
                with open(pdb_file_list[0], 'rb') as f:
                    zipf.writestr(f"{os.path.basename(pdb_file_list[0])}", f.read())
            else:
                for filename in pdb_file_list:
                    with open(filename, 'rb') as f:
                        zipf.writestr(f"data/Structure/{os.path.basename(filename)}", f.read())

        buffer.seek(0)  # 回到文件开头

        # 返回 FileResponse 给前端
        return FileResponse(buffer, as_attachment=True, filename='select.zip')

    @staticmethod
    def get_full_path(basename):
        base_path = "/data/Data/Structure/"
        name_dir = re.match(r'^(.*?)_at_', basename).group(1)
        logger.debug(f'namedir: {name_dir}')
        return f'{base_path}{name_dir}/{basename}.pdb'


    @staticmethod
    def get_sequence(seq_list):
        seq_ids = ','.join(seq_list)
        blast_cmd = [
            'blastdbcmd',
            '-db', '/tips_db/blast_db/all_db/all',
            '-entry', seq_ids,
            '-dbtype', 'prot'
        ]
        result = subprocess.run(blast_cmd, capture_output=True, text=True, check=True)
        return result.stdout
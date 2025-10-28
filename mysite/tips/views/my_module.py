import os
import shutil
import csv
import tempfile
from django.conf import settings
from django.db import connection
from tips.views.views import logger

class UuidManager:
    uuid_storage = {}
    @classmethod
    def add_entry(cls, uuid, file_type, file_path):
        """添加 UUID 相关的文件路径及配置信息"""
        if uuid not in cls.uuid_storage:
            cls.uuid_storage[uuid] = {}  # 创建新的 UUID 条目
        if file_type in cls.uuid_storage[uuid] and cls.uuid_storage[uuid][file_type]:
            existing_file_path = cls.uuid_storage[uuid][file_type]
            if os.path.exists(existing_file_path):  # 确保文件存在
                os.remove(existing_file_path)  # 删除旧文件
                logger.debug(f"The file {existing_file_path} exists, delete the file")

        cls.uuid_storage[uuid][file_type] = file_path  # 记录文件路径及配置
        logger.debug(f"Saved file in {file_path}")

    @classmethod
    def get_files_for_uuid(cls, uuid):
        """根据 UUID 获取关联的文件和配置信息"""
        return cls.uuid_storage.get(uuid, {})  # 返回 UUID 对应的文件信息

    @classmethod
    def delete_uuid_entry(cls, uuid):
        logger.debug(f'Current uuid: {uuid}')
        """删除 UUID 及其关联的所有文件信息"""
        if uuid in cls.uuid_storage and os.path.exists(f'{settings.TEMP_DIR}/{uuid}'):
            shutil.rmtree(f'{settings.TEMP_DIR}/{uuid}')
            del cls.uuid_storage[uuid]  # 删除 UUID 相关条目
        else:
            shutil.rmtree(f'{settings.TEMP_DIR}/{uuid}')
            logger.warning(f'The uuid {uuid} does not exist, but still try to delete the directory')

class FileReshape:
    @staticmethod
    def read_tsv_file(tsv_file_path, out_type, uuid):
        data = []
        with open(tsv_file_path, newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            with connection.cursor() as cursor:
                for row in reader:
                    basename = row['target']
                    query = "SELECT tips_id, description, species, tax_id, display FROM data_info WHERE basename = %s"
                    cursor.execute(query, (basename,))
                    result = cursor.fetchall()
                    if not result or not result[0][4]:
                        continue
                    row['target'] = result[0][0]
                    row['description'] = result[0][1]
                    row['scientificname'] = result[0][2]
                    row['taxid'] = result[0][3]
                    if out_type != 'mmseqs':
                        row['alntmscore'] = f"{round(min(float(row['alntmscore']), 1), 3):.3f}" #round(min(float(row['alntmscore']), 1), 3)
                    data.append(row)

        out_file_path = FileReshape.save_to_tsv(data, uuid)
        if out_type == 'mmseqs':
            UuidManager.add_entry(uuid, 'reshape_mmseq2_tsv', out_file_path)
        else:
            UuidManager.add_entry(uuid, 'reshape_foldseek_tsv', out_file_path)
        return data

    @staticmethod
    def save_to_tsv(data, uuid):
        if not data:
            print("No data to save.")
            return None

        # 获取字段名
        fieldnames = data[0].keys()
        with tempfile.NamedTemporaryFile(delete=False, dir=f'{settings.TEMP_DIR}/{uuid}',
                                         suffix='.tsv' , mode='w', encoding='utf-8') as temp_seq_file:
            writer = csv.DictWriter(temp_seq_file, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()  # 写入表头
            writer.writerows(data)  # 写入数据
        return temp_seq_file.name

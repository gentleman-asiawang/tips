from django.db import models
import os
from django.conf import settings

# Create your models here.
my_tree = None  # 在模块级别初始化

def load_tree():
    # 这里加载你的树，可能是从数据库或文件
    from ete3 import Tree
    global my_tree  # 使用全局变量存储树
    file_path = os.path.join(settings.BASE_DIR, 'tips', 'data', 'tree.nwk')
    my_tree = Tree(file_path)  # 假设你的树文件名为 tree.nwk

class DataInfo(models.Model):
    tips_id = models.CharField(max_length=13, primary_key=True)
    orders =  models.CharField(max_length=20)
    species = models.CharField(max_length=50)
    tax_id = models.CharField(max_length=20)
    basename = models.CharField(max_length=100)
    description =  models.TextField()
    display = models.BooleanField()
    class Meta:
        db_table = 'data_info'
        managed = False

class FileInfo(models.Model):
    tax_id = models.CharField(max_length=10, primary_key=True)
    size = models.CharField(max_length=30)
    count = models.CharField(max_length=10)
    filename = models.CharField(max_length=60, db_index=True)
    md5 = models.CharField(max_length=32)
    class Meta:
        db_table = 'file_info'
        managed = False
        indexes = [
            models.Index(fields=['filename'], name='idx_filename'),  # 显式定义索引
        ]
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
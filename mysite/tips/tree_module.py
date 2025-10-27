from ete3 import Tree
import os
from django.conf import settings

_my_tree = None

def get_tree():
    global _my_tree
    if _my_tree is None:
        file_path = os.path.join(settings.BASE_DIR, 'tips', 'data', 'tree.nwk')
        _my_tree = Tree(file_path)
    return _my_tree

def reload_tree():
    """强制重新加载树文件"""
    global _my_tree
    file_path = os.path.join(settings.BASE_DIR, 'tips', 'data', 'tree.nwk')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Tree file not found: {file_path}")
    _my_tree = Tree(file_path)
    return _my_tree
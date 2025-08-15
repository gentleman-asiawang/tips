from django.apps import AppConfig

class ApiTestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tips'

    def ready(self):
        from .models import load_tree  # 导入你加载树的函数
        load_tree()  # 调用函数以加载树

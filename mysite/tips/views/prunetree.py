import re
from ete3 import Tree
import json
from tips.models import load_tree, my_tree
from django.views import View
from django.db import connection
from django.http import JsonResponse, HttpResponse

from tips.views.views import logger


class PruneTree(View):
    @staticmethod
    def post(request):
        if request.headers.get('Content-Type') != 'application/json':
            return HttpResponse('Request header error!', status=400)
        data = json.loads(request.body)
        name_input = [name.strip() for name in data.get('species_names').splitlines() if name.strip()]
        logger.debug(name_input)
        wrong_value = []
        results_list = []
        with connection.cursor() as cursor:
            for name in name_input:
                query = ""
                if '_' in name and ' ' in name: # 输入含有'_'和' ',可以认为是输入错误了
                    wrong_value.append(name)
                    logger.debug('Have"_"and" "')
                elif '_' in name: # 只含有'_'，那么输入应该是tip_name或species
                    query = "SELECT tip_name FROM tree_info WHERE tip_name = %s"
                    cursor.execute(query, (name,))
                elif ' ' in name: # 只含有' '，将空格转为_同上进行查询
                    name = name.replace(' ', '_')
                    query = "SELECT tip_name FROM tree_info WHERE tip_name = %s"
                    cursor.execute(query, (name,))
                elif name.isdigit(): # 只含有数字，那么输入应该是taxid
                    query = "SELECT tip_name FROM tree_info WHERE tax_id = %s"
                    cursor.execute(query, (name,))
                else: # 不含有'_'和' ',那么输入应该是目名     不允许根据目提取树
                    wrong_value.append(name)
                    logger.debug('Do not allow prune by order')
                    # query = "SELECT tip_name FROM tree_info WHERE orders = %s"
                    # cursor.execute(query, (name,))

                if query:
                    results = cursor.fetchall()
                    for row in results:
                        results_list.append(row[0])


            if results_list:
                all_tree = my_tree.copy()
                duplicates = set(x for x in results_list if results_list.count(x) > 1)
                unique_values = list(set(results_list))
                all_tree.prune(unique_values)
                tree_text = all_tree.write(format=0)
                logger.debug(tree_text)
                if duplicates:
                    return JsonResponse({'warning': 'Duplicate values exist and are automatically ignored.',
                                         'duplicates': duplicates, 'tree': tree_text}, status=200)
                else:
                    return JsonResponse({'wrong_value': wrong_value, 'tree': tree_text}, status=200)
            else:
                return JsonResponse({'error': 'Subtree not found!', 'wrong_value': wrong_value}, status=400)



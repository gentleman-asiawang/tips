from tips.tree_module import get_tree
from tips.models import TreeInfo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from tips.views.views import logger


@api_view(['POST'])
def prune_tree(request):
    data = request.data
    species_names = data.get('species_names', '')
    name_input = [name.strip() for name in species_names.splitlines() if name.strip()]
    logger.debug(f'Input names: {name_input}')

    wrong_value = []
    results_list = []

    for name in name_input:
        query_set = None
        if '_' in name and ' ' in name:
            wrong_value.append(name)
            logger.debug('Have "_" and " "')
        elif '_' in name:
            query_set = TreeInfo.objects.filter(tip_name=name)
        elif ' ' in name:
            query_set = TreeInfo.objects.filter(tip_name=name.replace(' ', '_'))
        elif name.isdigit():
            query_set = TreeInfo.objects.filter(tax_id=name)
        else:
            wrong_value.append(name)
            logger.debug('Do not allow prune by order')

        if query_set:
            results_list.extend(query_set.values_list('tip_name', flat=True))

    if not results_list:
        return Response({'error': 'No matching species', 'wrong_value': wrong_value},
                        status=status.HTTP_400_BAD_REQUEST)

    tree = get_tree()
    if tree is None:
        return Response({'error': 'Tree not loaded on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        all_tree = tree.copy()
        duplicates = set(x for x in results_list if results_list.count(x) > 1)
        unique_values = list(set(results_list))
        all_tree.prune(unique_values)
        tree_text = all_tree.write(format=0)
        logger.debug(tree_text)
        if duplicates:
            return Response({
                'warning': 'Duplicate values exist and are automatically ignored.',
                'duplicates': list(duplicates),
                'tree': tree_text
            })
        else:
            return Response({
                'wrong_value': wrong_value,
                'tree': tree_text
            }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception('Error pruning tree:')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



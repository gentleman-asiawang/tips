from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from tips.views.querybyid import query_by_id
from tips.views.views import login, get_orders, ReceiveFileAPIView, delete_all_temp_files, GetServerLoadAPIView, get_file_info
from tips.views.file2ui import DownloadData, DownloadTable, GetPDBFile
from tips.views.querybypdb import *
from tips.views.querybysequence import query_by_sequence
from tips.views.prunetree import *

urlpatterns = [
    path('query_by_pdb/', csrf_exempt(QueryByPDB.as_view()), name='query_by_pdb'),
    path('query_by_sequence/', query_by_sequence, name='query_by_sequence'),
    path('query_by_id/', query_by_id, name='query_by_id'),
    path('get_pdb_file/', GetPDBFile.as_view(), name='get_pdb_file'),
    path('prune_tree/', prune_tree, name='prune_tree'),
    path('download_data/', DownloadData.as_view(), name='download_data'),
    path('download_table/', DownloadTable.as_view(), name='download_table'),
    path('delete_all_temp_files/', delete_all_temp_files, name="delete_temp_files"),
    path('receive_file/', ReceiveFileAPIView.as_view(), name="receive_file"),
    path('get_orders/', get_orders, name="get_orders"),
    path('get_file_info/', get_file_info, name="get_file_info"),
    path('login/', login, name='login'),
    path('get_server_load/', GetServerLoadAPIView.as_view(), name='get_server_load'),
]
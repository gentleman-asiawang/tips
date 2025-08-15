from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from tips.views.querybyid import *
from tips.views.views import *
from tips.views.file2ui import *
from tips.views.querybypdb import *
from tips.views.querybysequence import *
from tips.views.prunetree import *

urlpatterns = [
    path('query_by_pdb/', csrf_exempt(QueryByPDB.as_view()), name='query_by_pdb'),
    path('query_by_sequence/', csrf_exempt(QueryBySequence.as_view()), name='query_by_sequence'),
    path('query_by_id/', csrf_exempt(QueryById.as_view()), name='query_by_id'),
    path('get_pdb_file/', csrf_exempt(GetPDBFile.as_view()), name='get_pdb_file'),
    path('prune_tree/', csrf_exempt(PruneTree.as_view()), name='prune_tree'),
    path('download_data/', csrf_exempt(DownloadData.as_view()), name='download_data'),
    path('download_table/', csrf_exempt(DownloadTable.as_view()), name='download_table'),
    path('delete_all_temp_files/', csrf_exempt(DeleteAllTempFiles.as_view()), name="delete_temp_files"),
    path('receive_file/', csrf_exempt(ReceiveFile.as_view()), name="receive_file"),
    path('get_orders/', csrf_exempt(GetOrders.as_view()), name="get_orders"),
    path('get_file_info/', csrf_exempt(GetFileinfo.as_view()), name="get_file_info"),
    path('get_uuid/', csrf_exempt(GetUuid.as_view()), name='get_uuid'),
    path('get_server_load/', csrf_exempt(GetServerLoad.as_view()), name='get_server_load'),
]
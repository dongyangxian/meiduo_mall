from django.shortcuts import render
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
# Create your views here.
from goods.models import SKU
from goods.serializers import SKUSerializer, SKUSearchSerializer
from goods.utils import StandardResultsSetPagination


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    pagination_class = StandardResultsSetPagination  # 使用分页器
    filter_backends = [OrderingFilter]
    ordering_fields = ('price', 'create_time', 'sales')

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SKU.objects.filter(category_id=pk, is_launched=True)

class SKUSearchView(HaystackViewSet):
    """SKU搜索"""
    index_models = [SKU]
    serializer_class = SKUSearchSerializer
    pagination_class = StandardResultsSetPagination
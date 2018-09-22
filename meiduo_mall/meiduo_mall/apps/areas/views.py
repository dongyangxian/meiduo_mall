from django.shortcuts import render
from rest_framework.generics import ListAPIView

from areas.models import Area
from areas.serializers import AreasSerializer
# Create your views here.

class AreaView(ListAPIView):
    """省市区信息查询"""
    serializer_class = AreasSerializer
    # 添加查询集
    queryset = Area.objects.filter(parent=None)

class CityView(ListAPIView):
    """市区信息查询"""
    serializer_class = AreasSerializer
    # 查询市县的信息，需要重写get_query()
    def get_queryset(self):
        pk = self.kwargs['pk']   # 获取传送来的省或市的id
        return Area.objects.filter(parent=pk)

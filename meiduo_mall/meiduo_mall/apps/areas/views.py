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

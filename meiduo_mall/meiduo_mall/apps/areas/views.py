from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from areas.models import Area
from users.models import Address
from areas.serializers import AreasSerializer, AddressSerializer
# Create your views here.

class CreateAddressView(CreateAPIView):
    serializer_class = AddressSerializer
    """新增地址，及地址查询"""

    def get(self, request):
        # 获取用户
        user = self.request.user
        if not user:
            return Exception("用户未登录")
        # 获取地址
        address = Address.objects.filter(user=user, is_deleted=False)
        if not address:
            address = []
        # 序列化返回
        serializer = self.get_serializer(address, many=True)

        data = {
            "user_id": user.id,
            "default_address_id": user.default_address_id,
            "limit": 5,
            "addresses": serializer.data
        }

        return Response(data=data)

class AreaView(CacheResponseMixin, ListAPIView):
    """省市区信息查询"""
    serializer_class = AreasSerializer
    # 添加查询集
    queryset = Area.objects.filter(parent=None)

class CityView(CacheResponseMixin, ListAPIView):
    """市区信息查询"""
    serializer_class = AreasSerializer
    # 查询市县的信息，需要重写get_query()
    def get_queryset(self):
        pk = self.kwargs['pk']   # 获取传送来的省或市的id
        return Area.objects.filter(parent=pk)

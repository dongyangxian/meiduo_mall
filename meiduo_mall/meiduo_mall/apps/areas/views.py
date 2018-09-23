from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from areas.models import Area
from users.models import Address
from areas.serializers import AreasSerializer, AddressSerializer
# Create your views here.

class EditAddressView(viewsets.ViewSet):
    """收货地址编辑：标题修改/设为默认地址/内容修改/删除"""
    def title(self, request, id=None):
        """编辑地址标题"""
        # 1. 接收title及id
        title = request.data['title']

        # 2. 判断地址
        try:
            address = Address.objects.get(id=id)
        except:
            return Response({'data': '地址不存在'})

        # 3. 修改
        address.title = title
        address.save()
        # 4. 返回结果
        return Response({'data': 'Ok'})

    def update(self, request, id=None):
        # 接收内容（前端发送为json格式，用request.data）
        # request.data -> 前端发送内容
        # id判断
        try:
            address = Address.objects.get(id=id)
        except:
            return Response({'data': '地址不存在'})
        # 修改，保存(调用序列化器，进行数据更新操作)
        serializer = AddressSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 返回
        return Response(serializer.data, status=201)

    def destory(self, request, id=None):
        """地址删除"""
        # id判断
        try:
            address = Address.objects.get(id=id)
        except:
            return Response({'data': '地址不存在'})

        # 删除
        address.delete()

        # 返回数据
        return Response(status=204)


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

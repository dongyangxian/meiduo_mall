from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer


class OrderSettlementView(APIView):
    """订单展示
    思路：根据redis中获取到的数据，组建成cookie的数据格式，然后查询出对应的商品对象，进行序列化，最后返回
    """
    def get(self, request):
        # 链接redis
        conn = get_redis_connection('carts')
        user = request.user

        # 获取数据
        sku_id_count_dict = conn.hgetall('cart_%s' % user.id)
        sku_selected_list = conn.smembers('cart_selected_%s' % user.id)

        # 构建数据
        cart = {}

        for sku_id in sku_selected_list:
            cart[int(sku_id)] = int(sku_id_count_dict[sku_id])
        # 查询出对应的对象
        sku_list = SKU.objects.filter(id__in=cart.keys())

        # 添加运费属性
        freight = Decimal('10.00')
        for sku in sku_list:
            sku.count = cart[sku.id]

        # 进行序列化
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': sku_list})

        # 返回结果
        return Response(serializer.data)
import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartsSerializer, Cartserializers
from goods.models import SKU


class CartsView(APIView):
    """
    思路：
        用户未登录情况下，使用cookie来保存购物车信息：
                        cart:{
                                sku_id: { "count": xxx  // 数量 ,   "selected": True  // 是否勾选 },
                                sku_id: { "count": xxx  // 数量 ,   "selected": True  // 是否勾选 },
                            }
        用户登录情况下，使用redis保存信息：
                        Hash类型保存 cart_用户id : {商品id，对应商品的数量count}
                        Set类型保存  cart_selected_用户id : {已选择的商品id}

    """
    def perform_authentication(self, request):
        """重写用户认证方法，允许未登录的用户访问此接口"""
        pass

    def post(self, request):
        """保存商品信息到购物车"""
        # 1. 获取前端json数据
        data = request.data
        # 2. 序列化数据，并取出三个数据（sku_id, count, selected）
        serializer = CartsSerializer(data)
        sku_id = serializer.data['sku_id']
        count = serializer.data['count']
        selected = serializer.data['selected']
        # 3. 用户登录判断
        try:
            user = request.user
        except:
            user = None

        # 3.1 用户已登录
        if user is not None:
            # 3.1.1 链接数据库
            conn = get_redis_connection('carts')

            # 3.1.2 Hash类型保存
            conn.hincrby('cart_%s' % user.id, sku_id, count)
            # 3.1.3 Set类型保存
            if selected:
                conn.sadd('cart_selected%s' % user.id, sku_id)
            # 3.1.4 返回响应
            return Response(serializer.data)
        # 3.2 用户未登录
        else:
            # 3.2.1 获取cookie，并判断。为空置为{}
            cart_cookie = request.COOKIES.get('cart_cookie')
            # 3.2.2 如果存在，cookie解码，并判断是否存在响应商品，如果存在，数量增加
            if cart_cookie:
                # 解码
                cart = pickle.loads(base64.b64decode(cart_cookie.encode()))
                sku = cart[sku_id]
                if sku:
                    count += int(sku['count'])
            else:
                cart = {}

            # 3.2.3 组织商品数据形式
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 3.2.4 组织响应对象，加密，生成cookie，返回
            response = Response(serializer.data)
            cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response.set_cookie('cart_cookie', cart_cookie, 60*60*24)

            return response

    def get(self, request):
        """查询购物车的商品信息"""
        # 1. 获取用户，判断状态
        try:
            user = request.user
        except:
            user = None

        # 2. 用户登录状态
        if user is not None:
            # 2.1 连接数据库
            conn = get_redis_connection('carts')

            # 2.2 查询Hash类型数据
            sku_id_count_list = conn.hgetall('cart_%s' % user.id)

            # 2.3 查询Set类型数据
            sku_id_list = conn.smembers('cart_selected%s' % user.id)

            # 2.4 组织成cookie类型的数据
            cart = {}
            for sku_id, count in sku_id_count_list.items():
                cart[int(sku_id)] = {
                    'count': count,
                    'selected': sku_id in sku_id_list  # 如果sku_id存在于sku_selected就为True，否则为False
                }
        # 3. 用户未登录状态
        else:
            # 3.1 获取cookie，判断是否存在
            cart_cookie = request.COOKIES.get('cart_cookie')
            if cart_cookie:
                cart = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                # 3.2 如果不存在就置为{}
                cart = {}

        # 4. 查询所有的商品列表
        sku_list = SKU.objects.filter(id__in=cart.keys())

        # 5. 添加count和selected属性，以便进行序列化
        for sku in sku_list:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        # 6. 序列化数据
        serializer = Cartserializers(sku_list, many=True)

        # 7. 返回响应
        return Response(serializer.data)
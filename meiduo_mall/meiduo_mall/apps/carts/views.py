import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartsSerializer


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
                conn.sadd('cart_%s' % user.id, sku_id)
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
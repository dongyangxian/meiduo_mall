from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
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

    def get(self, request):
        """查询购物车的商品信息"""
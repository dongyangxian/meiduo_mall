from datetime import datetime

from decimal import Decimal
from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from django.db.transaction import atomic

class SaveOrderSerializer(serializers.ModelSerializer):
    """订单数据序列化"""
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            },
        }

    def create(self, validated_data):
        # 1. 获取用户
        user = self.context['request'].user
        # 2. 获取地址和支付方式
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 3. 生成订单编号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        # 4. 使用事物处理数据库操作
        with transaction.atomic():
            # 生成保存点对象
            save_point = transaction.savepoint()

            try:
                # 4.1 初始化订单对象
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method==2 else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 4.2 获取所有选中状态的商品
                # 建立链接
                conn = get_redis_connection('carts')
                # 从redis中获取sku_id和count，选中状态的sku_id
                sku_id_count = conn.hgetall('cart_%s' % user.id)
                cart_selected = conn.smembers('cart_selected_%s' % user.id)

                # 数据构建
                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(sku_id_count[sku_id])

                # 查询商品对象
                for sku_id in cart.keys():

                    while True:

                        # 查询数量及原始库存/销量
                        sku = SKU.objects.get(id=sku_id)

                        sku_count = cart[sku.id]  # 获取购买商品的数量
                        old_stock = sku.stock  # 获取原始库存量
                        old_sales = sku.sales  # 获取原始销量

                        # 判断库存
                        if sku_count > old_stock:
                            raise serializers.ValidationError('库存不足')

                        # 修改商品库存和销量
                        new_stock = old_stock - sku_count
                        new_sales = old_sales + sku_count

                        # TODO 使用乐观锁
                        ret = SKU.objects.filter(id=sku.id, stock=old_stock).update(stock=new_stock,sales=new_sales)
                        if ret == 0:  # 如果返回值为0,就说明数据已经被修改过了，需要重新去处理
                            continue

                        # 修改保存spu表和order表
                        sku.goods.sales += sku_count
                        sku.goods.save()

                        order.total_count += sku_count
                        order.total_amount += (sku.price * sku_count)

                        # 商品订单保存
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )

                        break

                    # 总价添加运费
                    order.total_amount += order.freight
                    order.save()
            except:
                transaction.savepoint_rollback(save_point)
            else:
                # 保存数据库的操作
                transaction.savepoint_commit(save_point)

                # 清除购物车中的缓存
                conn.hdel('cart_%s' % user.id, *cart_selected)

                conn.srem('cart_selected_%s' % user.id, *cart_selected)

                # 返回订单对象
                return order

class CartSKUSerializer(serializers.ModelSerializer):
    """订单结算数据展示"""
    count = serializers.IntegerField(read_only=True)
    class Meta:
        model = SKU
        fields = '__all__'

class OrderSettlementSerializer(serializers.Serializer):
    """订单结算数据展示-运费"""
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)
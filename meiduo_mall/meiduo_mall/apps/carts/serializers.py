from rest_framework import serializers

from goods.models import SKU


class CartsSerializer(serializers.Serializer):
    """商品信息添加到购物车"""
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField()
    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        """验证商品是否存在，及用户购买的数量是否大于库存量"""
        sku_id = attrs['sku_id']
        count = attrs['count']

        # 验证商品是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            raise serializers.ValidationError('商品不存在')

        # 验证数量是否大于库存量
        if count > sku.stock:
            raise serializers.ValidationError('商品不足')

        return attrs
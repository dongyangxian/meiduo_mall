from rest_framework import serializers

from goods.models import SKU


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
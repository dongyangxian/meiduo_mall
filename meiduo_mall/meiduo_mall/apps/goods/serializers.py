from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from goods.models import SKU
from goods.search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = '__all__'

class SKUSearchSerializer(HaystackSerializer):
    """SKU索引结果数据序列化器"""
    object = SKUSerializer()
    class Meta:
        index_classes = [SKUIndex]  # 指定索引模型类
        fields = ('text', 'object')

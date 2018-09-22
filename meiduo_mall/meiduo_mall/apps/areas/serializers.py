from rest_framework import serializers
from areas.models import Area
class AreasSerializer(serializers.ModelSerializer):
    """省市区序列化器"""
    class Meta:
        model = Area
        fields = ('id', 'name')

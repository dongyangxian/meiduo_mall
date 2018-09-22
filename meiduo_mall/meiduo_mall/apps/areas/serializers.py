import re

from rest_framework import serializers
from areas.models import Area
from users.models import Address
class AreasSerializer(serializers.ModelSerializer):
    """省市区序列化器"""
    class Meta:
        model = Area
        fields = ('id', 'name')


class AddressSerializer(serializers.ModelSerializer):
    # 地址添加字段
    province_id = serializers.IntegerField(required=True)
    city_id = serializers.IntegerField(required=True)
    district_id = serializers.IntegerField(required=True)

    # 外键序列化
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate(self, attrs):
        # 对手机号进行验证
        if not re.match(r'^1[3-9]\d{9}$', attrs['mobile']):
            raise serializers.ValidationError('手机号格式错误')
        return attrs

    def create(self, validated_data):
        # 获取用户id
        user = self.context['request'].user

        # 继承父类，新增地址
        validated_data['user'] = user
        address = super().create(validated_data)

        # 返回用户
        return address


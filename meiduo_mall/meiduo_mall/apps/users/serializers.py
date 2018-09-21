import re

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from rest_framework_jwt.settings import api_settings

class UserEmailSerializer(serializers.ModelSerializer):
    """保存邮箱，发送邮件"""
    class Meta:
        model = User
        fields = ('id', 'email')

    def update(self, instance, validated_data):
        # 1. 用于序列化时，将模型类对象传入instance参数
        # 2. 用于反序列化时，将要被反序列化的数据传入data参数
        # 保存邮箱，并发送
        user = instance
        user.email = validated_data['email']
        user.save()

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    """用户个人中心展示"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')

class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password2 = serializers.CharField(label='确认密码', max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    # 定义token字段
    token = serializers.CharField(label='登录状态token', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'mobile', 'username', 'password', 'password2', 'sms_code', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字过长',
                    'min_length': '名字过短'
                }
            },
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'error_messages': {
                    'max_length': '密码过长',
                    'min_length': '密码过短'
                }
            },
        }

    # 验证
    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}$', value):
            return serializers.ValidationError('手机格式不正确')
        return value

    # 判断是否选中协议
    def validate_allow(self, value):

        if value != 'true':
            return serializers.ValidationError('未选中')

        return value

    def validate(self, attrs):
        # 密码判断

        if attrs['password'] != attrs['password2']:
            return serializers.ValidationError('密码不一致')

        # 判断短信
        # 1 先获取缓存中短信
        conn = get_redis_connection('verify')
        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])

        if not real_sms_code:
            return serializers.ValidationError('短信验证码失效')

        if attrs['sms_code'] != real_sms_code.decode():
            return serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        # 删除多余字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # 保存数据
        user = super().create(validated_data)
        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        # 写入token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        # 返回值
        return user

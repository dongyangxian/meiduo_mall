from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.conf import settings
from rest_framework.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User


class OAuthQQSerializer(serializers.Serializer):
    """未绑定用户的绑定处理"""
    mobile = serializers.RegexField(max_length=11, regex='^1[5-9]\d{9}$')
    password = serializers.CharField(min_length=8, max_length=20, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(write_only=True)
    username = serializers.CharField(read_only=True)

    # 验证
    def validate(self, attrs):

        # TODO 获取access_token（因为未绑定时，在get中返回的名字就是access_token，但里面包的是openid），进行判断。如果存在，则进行解码，取出openid
        tjs = TJS(settings.SECRET_KEY, 300)

        # 1.1 获取access_token
        try:
            data = tjs.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('错误的access_token')

        # 1.2 获取openid
        openid = data.get('openid')

        # 判断openid是否存在。不存在，表示过期。存在，就给attrs添加openid属性
        if not openid:
            raise serializers.ValidationError('access_token失效')
        attrs['openid'] = openid

        # TODO 短信验证
        # 1 连接，获取缓存中短信，进行判断验证
        conn = get_redis_connection('verify')
        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])

        if not real_sms_code:
            return serializers.ValidationError('短信验证码失效')

        if attrs['sms_code'] != real_sms_code.decode():
            return serializers.ValidationError('短信验证码错误')

        # TODO 用户验证
        # 如果已经存在，表示已经注册过，再验证密码是否正确。否则，直接返回attrs
        try:
            user = User.objects.get(mobile=attrs['mobile'])
            if user and user.check_password(attrs['password']):
                attrs['user'] = user
                return attrs
            raise serializers.ValidationError('密码不正确')
        except:
            return attrs

    # 创建用户
    def create(self, validated_data):
        # 1. 获取用户，判断是否存在.不存在就创建新的用户
        user = validated_data.get('user', None)
        if not user:
            user = User.objects.create_user(username=validated_data['mobile'],
                                            mobile=validated_data['mobile'],
                                            password=validated_data['password'],
                                            )
        # 2. 进行绑定
        OAuthQQUser.objects.create(user=user,
                                   openid=validated_data['openid'],
                                   )
        # 3. 组织返回token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        # 4. 返回user
        return user




from django.conf import settings
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
import random
# Create your views here.

# get 127.0.0.1/register/18011112222
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView
from users.serializers import CreateUserSerializer, UserDetailSerializer, UserEmailSerializer, \
    AddUserBrowsingHistorySerializers
from celery_tasks.sms.tasks import send_sms_code
from meiduo_mall.libs.yuntongxun.sms import CCP
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from users.models import User

class AddUserBrowsingHistoryView(CreateAPIView):
    """
    思路：
        当用户进入商品的详情页时，保存商品的id到redis中。
        但是，由于默认存储在mysql中，所以在create方法中要重写
    """
    serializer_class = AddUserBrowsingHistorySerializers

class VerifyEmailView(APIView):
    """邮箱验证"""
    def get(self, request):
        """
        思路：前端会携带着包含有用户id和username的token，
             后台只需获取到里面的数据，加以判断，然后更改email_active的状态即可
        :return:
        """
        # 1. 获取token，判断
        token = request.query_params.get("token")
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 2. 解码
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            raise Exception('错误的token')

        # 3. 判断是否存在用户
        try:
            user = User.objects.get(id=data['id'], username=data['username'])
        except:
            # 如果不存在，说明token无效
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)

        # 4. 如果存在就修改email_active
        user.email_active = True
        user.save()

        return Response({'message': 'OK'})

class UserEmailView(UpdateAPIView):
    """保存邮箱，并发送邮件"""
    serializer_class = UserEmailSerializer
    def get_object(self):
        """因为前端没有传关于用户的信息，所以底层的方法无法获取到用户，只能重写方法，利用self.request来获取"""
        return self.request.user

class UserDetailView(RetrieveAPIView):
    """个人中心展示"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]  # 添加权限
    def get_object(self):
        return self.request.user

class UserView(CreateAPIView):
    """用户注册接口"""
    serializer_class = CreateUserSerializer

# mobiles/(?P<mobile>1[3-9]\d{9})/count
class UserMobileView(APIView):
    def get(self, request, mobile):
        # 查询是否存在
        count = User.objects.filter(mobile=mobile).count()
        # 结果处理
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)

# usernames/(?P<username>\w{5,20})/count/
class UserNameView(APIView):
    def get(self, request, username):
        # 查询是否存在
        count = User.objects.filter(username=username).count()
        # 结果处理
        data = {
            "username": username,
            "count": count
        }
        return Response(data)

class SMSCodeView(GenericAPIView):

    def get(self, request, mobile):
        # 验证
        conn = get_redis_connection('verify')
        flag = conn.get('sms_flag_%s' % mobile)
        if flag:
            return Response({"message": "error"})
        # 生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存到redis
        # 使用管道优化redis存储短信
        p1 = conn.pipeline()
        p1.setex('sms_code_%s' % mobile, 300, sms_code)
        p1.setex('sms_flag_%s' % mobile, 60, 1)
        p1.execute()
        print(sms_code)
        # 发送短信
        send_sms_code.delay(mobile, sms_code)
        # 返回响应
        return Response({"message": "OK"})

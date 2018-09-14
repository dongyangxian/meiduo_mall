from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
import random
# Create your views here.

# get 127.0.0.1/register/18011112222
from rest_framework.response import Response

from meiduo_mall.libs.yuntongxun.sms import CCP


class SMSCodeView(GenericAPIView):

    def get(self, request, mobile):
        # 验证
        conn = get_redis_connection('verify')
        flag = conn.get('sms_code_%s' % mobile)
        if flag:
            return Response({"message": "error"})
        # 生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存到redis

        conn.setex('sms_code_%s' % mobile, 300, sms_code)
        print(sms_code)
        # 发送短信
        # CCP().send_template_sms(mobile, [sms_code, '5'], 1)
        # 返回响应
        return Response({"message": "OK"})

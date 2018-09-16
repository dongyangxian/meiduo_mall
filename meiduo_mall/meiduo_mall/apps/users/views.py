from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
import random
# Create your views here.

# get 127.0.0.1/register/18011112222
from rest_framework.response import Response

from celery_tasks.sms.tasks import send_sms_code
from meiduo_mall.libs.yuntongxun.sms import CCP


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
        send_sms_code(mobile, sms_code)
        # 返回响应
        return Response({"message": "OK"})

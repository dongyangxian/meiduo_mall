import os

from alipay import AliPay
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo
from payments.serializers import Payment


class PaymentStatusView(APIView):
    """
    支付结果
    """
    def put(self, request):
        data = request.query_params.dict()
        signature = data.pop("sign")

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        success = alipay.verify(data, signature)
        if success:
            # 订单编号
            order_id = data.get('out_trade_no')
            # 支付宝支付流水号
            trade_id = data.get('trade_no')
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            OrderInfo.objects.filter(order_id=order_id).update(status=2)
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)

class PaymentView(APIView):
    """发起支付"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id):
        # # 1. 验证订单编号
        try:
            order = OrderInfo.objects.get(user=request.user, order_id=order_id, pay_method=2)
        except:
            return Response({'errors': '订单不存在'}, status=401)

        # 2. 构建跳转链接
        # 2.1 初始化操作
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 2.2 构造查询字符串
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )

        # 拼接url
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return Response({'alipay_url': alipay_url})
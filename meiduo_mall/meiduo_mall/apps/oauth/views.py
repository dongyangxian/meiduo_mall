from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

class QQLoginURLView(APIView):
    """
    点击登录时，发送请求到后台，生成一个url地址，进入到qq服务器的扫码登录界面
    """
    def get(self, request):

        # 获取前端传递的next
        next = request.query_params.get('next')
        if not next:
            next = '/'

        # 初始化OAuthQQ对象
        oauth = OAuthQQ(
                        client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next
                        )
        # 获取qq登录扫码页面，及qq的登录地址
        login_url = oauth.get_qq_url()

        # 返回url
        return Response({
            "login_url": login_url
        })


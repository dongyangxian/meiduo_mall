import requests
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
# Create your views here.
from oauth.models import OAuthQQUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from oauth.serializers import OAuthQQSerializer


class QQAuthUserView(CreateAPIView):

    serializer_class = OAuthQQSerializer
    def get(self, request):
        # 1. 获取前端传来的code
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code值'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. 根据code获取access_token(需要这个初始化对象)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        access_token = oauth.get_access_token(code)
        # 3. 获取open_id
        openid = oauth.get_open_id(access_token)

        # 4. 根据openid 去模型表中进行判断。
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:
            # 如果报错，就说明没有绑定，那就进行加密，然后返回
            tjs = TJS(settings.SECRET_KEY, 300)  # 使用TJS进行加密
            token = tjs.dumps({'openid': openid}).decode()
            return Response({'access_token': token})  # TODO 这里的token并不是JWT验证的，而是前端接收时的对应变量名称

        # 如果存在表示，已经绑定过。获取用户，并返回token值
        user = qq_user.user
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response({
            "username": user.username,
            "user_id": user.id,
            "token": token
        })
    # def post(self, request):
    #     # 获取前端表单数据
    #     # 验证
    #     # 获取access_token（因为未绑定时，在get中返回的名字就是access_token，但里面包的是openid），进行判断。如果存在，则进行解码，取出openid
    #     # 判断openid是否存在。不存在，表示过期。存在，就给attrs添加openid属性
    #     # 短信验证
    #     # 用户验证
    #     # 创建用户
    #     pass



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


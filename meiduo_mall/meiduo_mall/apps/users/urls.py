from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UserNameView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.UserMobileView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^emails/$', views.UserEmailView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]

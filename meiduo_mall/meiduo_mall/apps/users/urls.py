from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UserNameView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.UserMobileView.as_view()),
]

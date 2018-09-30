from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
]
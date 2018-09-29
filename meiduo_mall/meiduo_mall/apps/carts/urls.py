from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^cart/$', views.CartsView.as_view()),
    url(r'^cart/selection/$', views.CartSelectAllView.as_view()),
]
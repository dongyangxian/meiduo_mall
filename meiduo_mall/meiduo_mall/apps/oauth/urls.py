from django.conf.urls import url

from oauth import views

urlpatterns = [
    url(r'^qq/authorization/$', views.QQLoginURLView.as_view()),
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
]
from django.conf.urls import url
from .views import AreaView, CityView
from .views import CreateAddressView, EditAddressView
urlpatterns = [
    url(r'^areas/$', AreaView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', CityView.as_view()),
    url(r'^addresses/$', CreateAddressView.as_view()),

    url(r'^addresses/(?P<id>\d+)/title/$', EditAddressView.as_view({'put': 'title'})),  # 编辑标题  put
    url(r'^addresses/(?P<id>\d+)/status/$', EditAddressView.as_view({'put': 'default_address'})),  # 设为默认地址  put
    url(r'^addresses/(?P<id>\d+)/$', EditAddressView.as_view({'put': 'update', 'delete': 'destory'})),  # 地址修改/删除  put
    # url(r'^addresses/(?P<id>\d+)/$', EditAddressView.as_view({})),  # 地址删除  delete
]
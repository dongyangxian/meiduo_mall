from django.conf.urls import url
from .views import AreaView, CityView
from .views import CreateAddressView
urlpatterns = [
    url(r'^areas/$', AreaView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', CityView.as_view()),
    url(r'^addresses/$', CreateAddressView.as_view()),
]
from django.conf.urls import url
from .views import AreaView, CityView
urlpatterns = [
    url(r'^areas/$', AreaView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', CityView.as_view()),
]
from django.conf.urls import url
from .views import AreaView
urlpatterns = [
    url(r'^areas/$', AreaView.as_view())
]
from django.conf.urls import url
from .views import SKUListView
urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/skus/', SKUListView.as_view()),
]
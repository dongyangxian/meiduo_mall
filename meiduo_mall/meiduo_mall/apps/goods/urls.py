from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import SKUListView, SKUSearchView
urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/skus/', SKUListView.as_view()),
]

router = DefaultRouter()
router.register('skus/search', SKUSearchView, base_name='skus_search')
urlpatterns += router.urls
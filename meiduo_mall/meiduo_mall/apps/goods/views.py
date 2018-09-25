from django.shortcuts import render
from rest_framework.generics import ListAPIView
# Create your views here.
from goods.models import SKU
from goods.serializers import SKUSerializer


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SKU.objects.filter(category_id=pk, is_launched=True)
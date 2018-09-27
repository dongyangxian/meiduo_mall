from django.contrib import admin
from celery_tasks.static_html.tasks import generate_static_list_search_html, generate_static_sku_detail_html
# Register your models here.
from goods import models

class Goods(admin.ModelAdmin):
    list_display = ['id', 'name']

class SKUModelAdmin(admin.ModelAdmin):
    """后台创建商品时，增加商品的静态详情页"""
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)

admin.site.register(models.Goods)
admin.site.register(models.GoodsCategory, Goods)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUModelAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)

class GoodsCategoryModelAdmin(admin.ModelAdmin):
    list_per_page = 10
    def save_model(self, request, obj, form, change):
        print(obj)

        print(type(obj))

        obj.save()

    # 调用生成静态页面方法
    generate_static_list_search_html.delay()

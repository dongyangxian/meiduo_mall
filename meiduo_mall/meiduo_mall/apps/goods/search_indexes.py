from haystack import indexes
from goods.models import SKU

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """通过索引类来指定哪个模型类的字段数据建立索引"""
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)
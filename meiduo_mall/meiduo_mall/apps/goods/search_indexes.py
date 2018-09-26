from haystack import indexes
from goods.models import SKU

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """通过索引类来指定哪个模型类的字段数据建立索引"""
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
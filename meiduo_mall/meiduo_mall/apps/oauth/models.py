from django.db import models

# Create your models here.
from meiduo_mall.utils.models import BaseModel


class OAuthQQUser(BaseModel):
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)  # db_index添加为索引
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        db_table = 'db_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

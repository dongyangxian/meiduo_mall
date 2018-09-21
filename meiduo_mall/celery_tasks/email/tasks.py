import logging

from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app

logger = logging.getLogger('django')


@app.task(name='send_email')
def send_email(token, email):
    """
        发送短信验证码
        :param token: 手机号
        :param email: 验证码
        :return: None
        """
    verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

    try:
        send_mail(subject, "", settings.EMAIL_FROM, [email], html_message=html_message)
    except Exception as e:
        logger.error("发送邮件[异常][ email: %s, message: %s ]" % (email, e))
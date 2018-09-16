import logging

from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP

logger = logging.getLogger("django")

@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    try:
        result = CCP().send_template_sms(mobile, [sms_code, '5'], 1)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)

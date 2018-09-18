import re
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }
class MobileNameView(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断username是否为手机
        try:
            if re.match(r'1[3-9]\d{9}$', username):
                user = User.objects.get(Q(mobile=username) | Q(username=username))
            else:
                user = User.objects.get(username=username)
        except:
            user = None

        if user is not None and user.check_password(password):
            return user
        return user
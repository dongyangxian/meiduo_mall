import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    cart_cookie = request.COOKIES.get('cart_cookie')
    if not cart_cookie:
        return response
    # 解码
    cart = pickle.loads(base64.b64decode(cart_cookie.encode()))

    # 拆分数据
    sku_count_list = {}  # 保存{sku_id:count，sku_id:count，}
    sku_selected_list = []
    sku_selected_no_list = []

    if cart:
        for sku_id, count_dict in cart.items():
            sku_count_list[int(sku_id)] = int(count_dict['count'])
            if count_dict['selected']:
                sku_selected_list.append(sku_id)
            else:
                sku_selected_no_list.append(sku_id)
        # 替换数据
        conn = get_redis_connection('carts')
        conn.hmset('cart_%s' % user.id, sku_count_list)
        if sku_selected_list:
            conn.sadd('cart_selected_%s' % user.id, *sku_selected_list)
        if sku_selected_no_list:
            conn.sadd('cart_selected_%s' % user.id, *sku_selected_no_list)

    # 删除cookie
    response.delete_cookie('cart_cookie')
    # 返回响应
    return response
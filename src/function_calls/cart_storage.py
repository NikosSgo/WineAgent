carts = {}


def get_cart(thread_id):
    """Получить корзину для thread или создать новую"""
    print(carts)
    if thread_id not in carts:
        carts[thread_id] = []
    return carts[thread_id]


def clear_cart(thread_id):
    """Очистить корзину"""
    if thread_id in carts:
        del carts[thread_id]

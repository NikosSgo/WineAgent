from pydantic import BaseModel
from .cart_storage import clear_cart


class ClearCart(BaseModel):
    """Эта функция очищает корзину"""

    def process(self, thread):
        clear_cart(thread.id)
        return "Корзина очищена"

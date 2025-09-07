from pydantic import BaseModel
from .cart_storage import get_cart


class ShowCart(BaseModel):
    """Эта функция позволяет показать содержимое корзины"""

    def process(self, thread):
        cart = get_cart(thread.id)
        if len(cart) == 0:
            return "Корзина пуста"

        total_bottles = sum(item.count for item in cart)
        result = ["В корзине находятся следующие вина:"]

        for i, item in enumerate(cart, 1):
            result.append(f"{i}. {item.wine_name} - {item.count} бутылок")

        result.append(f"\nВсего бутылок: {total_bottles}")
        return "\n".join(result)

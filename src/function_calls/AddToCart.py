from pydantic import BaseModel, Field
from .cart_storage import get_cart


class AddToCart(BaseModel):
    """Эта функция позволяет положить или добавить вино в корзину"""

    wine_name: str = Field(
        description="Точное название вина, чтобы положить в корзину", default=None
    )
    count: int = Field(
        description="Количество бутылок вина, которое нужно положить в корзину",
        default=1,
    )

    def process(self, thread):
        cart = get_cart(thread.id)
        for item in cart:
            if item.wine_name == self.wine_name:
                item.count += self.count
                return f"Добавлено {self.count} бутылок вина {self.wine_name}. Теперь в корзине: {item.count} бутылок"

        cart.append(self)
        return f"Вино {self.wine_name} добавлено в корзину, число бутылок: {self.count}"

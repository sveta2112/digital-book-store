from decimal import Decimal

from cart import Cart
from catalog import DigitalBook
from errors import BookStoreError


class OrderItem:
    """Позиция заказа с названием и ценой на момент оформления."""

    def __init__(self, book: DigitalBook) -> None:
        self.book = book
        self.book_title = book.title
        self.purchase_price = book.price


class Order:
    """Заказ покупателя."""

    def __init__(self, order_id: int, cart: Cart) -> None:
        if order_id <= 0:
            raise ValueError(
                "Идентификатор заказа должен быть положительным."
            )

        cart_items = cart.get_items()
        if not cart_items:
            raise BookStoreError(
                "Нельзя оформить заказ с пустой корзиной."
            )

        for item in cart_items:
            if cart.customer.has_book(item.book.id):
                raise BookStoreError(
                    f"Книга «{item.book.title}» уже приобретена."
                )

        self.id = order_id
        self.customer = cart.customer
        self.status = "created"
        self._items = [
            OrderItem(item.book)
            for item in cart_items
        ]

    def get_items(self) -> list[OrderItem]:
        """Получить список позиций заказа."""
        return list(self._items)

    def get_total(self) -> Decimal:
        """Посчитать сумму по ценам на момент оформления."""
        return sum(
            (item.purchase_price for item in self._items),
            start=Decimal("0.00"),
        )

    def mark_paid(self) -> None:
        """Отметить созданный заказ как оплаченный."""
        if self.status != "created":
            raise BookStoreError(
                "Оплатить можно только созданный заказ."
            )

        self.status = "paid"

    def cancel(self) -> None:
        """Отменить созданный неоплаченный заказ."""
        if self.status != "created":
            raise BookStoreError(
                "Отменить можно только созданный неоплаченный заказ."
            )

        self.status = "cancelled"
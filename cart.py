from decimal import Decimal

from catalog import DigitalBook
from customers import Customer
from errors import BookStoreError


class CartItem:
    """Одна цифровая книга в корзине."""

    def __init__(self, book: DigitalBook) -> None:
        self.book = book

    def get_price(self) -> Decimal:
        """Получить текущую цену книги."""
        return self.book.price


class Cart:
    """Корзина выбранных книг покупателя."""

    def __init__(self, customer: Customer) -> None:
        self.customer = customer
        self._items: dict[int, CartItem] = {}

    def add_book(self, book: DigitalBook) -> None:
        """Добавить книгу, если она ещё не приобретена и не в корзине."""
        if self.customer.has_book(book.id):
            raise BookStoreError(
                f"Книга «{book.title}» уже приобретена."
            )

        if book.id in self._items:
            raise BookStoreError(
                f"Книга «{book.title}» уже находится в корзине."
            )

        self._items[book.id] = CartItem(book)

    def remove_book(self, book_id: int) -> None:
        """Удалить книгу из корзины."""
        if book_id not in self._items:
            raise BookStoreError(
                f"Книга с идентификатором {book_id} отсутствует в корзине."
            )

        del self._items[book_id]

    def get_items(self) -> list[CartItem]:
        """Получить список позиций корзины."""
        return list(self._items.values())

    def get_total(self) -> Decimal:
        """Посчитать стоимость всех книг в корзине."""
        return sum(
            (item.get_price() for item in self._items.values()),
            start=Decimal("0.00"),
        )

    def clear(self) -> None:
        """Удалить все позиции из корзины."""
        self._items.clear()
from datetime import datetime
from decimal import Decimal

from errors import BookStoreError
from orders import Order, OrderItem


class Payment:
    """Учебная имитация оплаты заказа."""

    def __init__(self, payment_id: int, order: Order) -> None:
        if payment_id <= 0:
            raise ValueError(
                "Идентификатор платежа должен быть положительным."
            )

        if order.status != "created":
            raise BookStoreError(
                "Создать платёж можно только для нового заказа."
            )

        self.id = payment_id
        self.order = order
        self.amount: Decimal = order.get_total()
        self.status = "pending"

    def process(self, success: bool = True) -> bool:
        """Имитировать оплату; после неудачи разрешена новая попытка."""
        if self.status == "succeeded":
            raise BookStoreError("Этот платёж уже выполнен.")

        if self.order.status != "created":
            raise BookStoreError(
                "Оплатить можно только созданный заказ."
            )

        if not success:
            self.status = "failed"
            return False

        self.order.mark_paid()
        self.status = "succeeded"
        return True


class PurchaseLicense:
    """Право покупателя на доступ к книге из оплаченного заказа."""

    def __init__(
        self,
        license_id: int,
        order: Order,
        item: OrderItem,
    ) -> None:
        if license_id <= 0:
            raise ValueError(
                "Идентификатор права доступа должен быть положительным."
            )

        if order.status != "paid":
            raise BookStoreError(
                "Доступ к книге выдаётся только после оплаты заказа."
            )

        if item not in order.get_items():
            raise BookStoreError(
                "Позиция не принадлежит указанному заказу."
            )

        self.id = license_id
        self.order = order
        self.item = item
        self.customer = order.customer
        self.book = item.book
        self.issued_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

    def get_file_path(self) -> str:
        """Получить путь к файлу приобретённой книги."""
        return self.book.file_path
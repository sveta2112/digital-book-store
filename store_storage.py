import json
from datetime import datetime
from decimal import Decimal, DecimalException
from pathlib import Path
from typing import Any

from cart import Cart
from catalog_storage import CatalogCodec
from customers import Customer
from errors import BookStoreError
from orders import Order
from purchases import Payment, PurchaseLicense
from store import BookStore


class StoreCodec:
    """Преобразование состояния магазина в словарь и обратно."""

    @staticmethod
    def to_dict(store: BookStore) -> dict[str, Any]:
        """Подготовить все данные магазина для сохранения."""
        return {
            "version": 1,
            "catalog": CatalogCodec.to_dict(store.catalog),
            "customers": [
                {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                }
                for customer in store._customers.values()
            ],
            "carts": [
                {
                    "customer_id": customer_id,
                    "book_ids": [
                        item.book.id
                        for item in cart.get_items()
                    ],
                }
                for customer_id, cart in store._carts.items()
            ],
            "orders": [
                {
                    "id": order.id,
                    "customer_id": order.customer.id,
                    "status": order.status,
                    "items": [
                        {
                            "book_id": item.book.id,
                            "book_title": item.book_title,
                            "purchase_price": str(item.purchase_price),
                        }
                        for item in order.get_items()
                    ],
                }
                for order in store._orders.values()
            ],
            "payments": [
                {
                    "id": payment.id,
                    "order_id": payment.order.id,
                    "amount": str(payment.amount),
                    "status": payment.status,
                }
                for payment in store._payments.values()
            ],
            "licenses": [
                {
                    "id": license_record.id,
                    "order_id": license_record.order.id,
                    "book_id": license_record.book.id,
                    "issued_at": license_record.issued_at,
                }
                for license_record in store._licenses.values()
            ],
        }

    @staticmethod
    def read_money(record: dict[str, Any], key: str) -> Decimal:
        """Проверить денежное значение из файла."""
        value = Decimal(CatalogCodec.read_text(record, key))

        if not value.is_finite() or value < 0:
            raise ValueError(
                f"Поле «{key}» должно содержать конечную "
                "неотрицательную сумму."
            )

        if value % Decimal("0.01") != 0:
            raise ValueError(
                f"Поле «{key}» содержит доли меньше копейки."
            )

        return value

    @staticmethod
    def read_book_ids(record: dict[str, Any]) -> list[int]:
        """Проверить список идентификаторов книг корзины."""
        values = record["book_ids"]
        if not isinstance(values, list):
            raise ValueError("Поле «book_ids» должно быть списком.")

        for value in values:
            if type(value) is not int or value <= 0:
                raise ValueError(
                    "Идентификаторы книг должны быть "
                    "положительными целыми числами."
                )

        return values

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BookStore:
        """Проверить данные и восстановить новый магазин."""
        codec = CatalogCodec

        try:
            if not isinstance(data, dict):
                raise ValueError("Корень документа должен быть объектом.")

            if type(data.get("version")) is not int:
                raise ValueError("Версия должна быть целым числом.")

            if data["version"] != 1:
                raise ValueError("Неподдерживаемая версия формата.")

            store = BookStore()
            store.catalog = codec.from_dict(data["catalog"])

            for record in codec.read_records(data, "customers"):
                customer = Customer(
                    codec.read_id(record, "id"),
                    codec.read_text(record, "name"),
                    codec.read_text(record, "email"),
                )
                store.add_customer(customer)

            order_statuses: dict[int, str] = {}

            for record in codec.read_records(data, "orders"):
                order_id = codec.read_id(record, "id")
                if order_id in store._orders:
                    raise ValueError(
                        "Повторяющийся идентификатор заказа."
                    )

                customer = store.get_customer(
                    codec.read_id(record, "customer_id")
                )

                status = codec.read_text(record, "status")
                if status not in ("created", "paid", "cancelled"):
                    raise ValueError("Неизвестный статус заказа.")

                item_records = codec.read_records(record, "items")
                temporary_cart = Cart(customer)

                for item_record in item_records:
                    book = store.catalog.get_book(
                        codec.read_id(item_record, "book_id")
                    )
                    temporary_cart.add_book(book)

                order = Order(order_id, temporary_cart)

                for item, item_record in zip(
                    order.get_items(),
                    item_records,
                ):
                    title = codec.read_text(
                        item_record,
                        "book_title",
                    )
                    if not title.strip():
                        raise ValueError(
                            "Название книги в заказе не может быть пустым."
                        )

                    item.book_title = title
                    item.purchase_price = cls.read_money(
                        item_record,
                        "purchase_price",
                    )

                store._orders[order_id] = order
                order_statuses[order_id] = status

            payment_ids: set[int] = set()

            for record in codec.read_records(data, "payments"):
                payment_id = codec.read_id(record, "id")
                order_id = codec.read_id(record, "order_id")

                if payment_id in payment_ids:
                    raise ValueError(
                        "Повторяющийся идентификатор платежа."
                    )

                if order_id in store._payments:
                    raise ValueError(
                        "У одного заказа не может быть несколько платежей."
                    )

                order = store.get_order(order_id)
                status = codec.read_text(record, "status")

                if status not in ("pending", "failed", "succeeded"):
                    raise ValueError("Неизвестный статус платежа.")

                amount = cls.read_money(record, "amount")
                if amount != order.get_total():
                    raise ValueError(
                        "Сумма платежа не совпадает с суммой заказа."
                    )

                if status == "succeeded":
                    if order_statuses[order_id] != "paid":
                        raise ValueError(
                            "Успешный платёж связан "
                            "с неоплаченным заказом."
                        )
                elif order_statuses[order_id] == "paid":
                    raise ValueError(
                        "Оплаченный заказ не имеет успешного платежа."
                    )

                payment = Payment(payment_id, order)
                payment.status = status
                store._payments[order_id] = payment
                payment_ids.add(payment_id)

            for order_id, status in order_statuses.items():
                order = store.get_order(order_id)

                if status == "paid":
                    payment = store._payments.get(order_id)
                    if (
                        payment is None
                        or payment.status != "succeeded"
                    ):
                        raise ValueError(
                            "У оплаченного заказа отсутствует "
                            "успешный платёж."
                        )
                    order.mark_paid()

                elif status == "cancelled":
                    order.cancel()

            licensed_items: set[tuple[int, int]] = set()

            for record in codec.read_records(data, "licenses"):
                license_id = codec.read_id(record, "id")
                order_id = codec.read_id(record, "order_id")
                book_id = codec.read_id(record, "book_id")

                if license_id in store._licenses:
                    raise ValueError(
                        "Повторяющийся идентификатор права доступа."
                    )

                item_key = (order_id, book_id)
                if item_key in licensed_items:
                    raise ValueError(
                        "Повторное право доступа к позиции заказа."
                    )

                order = store.get_order(order_id)
                item = next(
                    (
                        item
                        for item in order.get_items()
                        if item.book.id == book_id
                    ),
                    None,
                )

                if item is None:
                    raise ValueError(
                        "Право доступа ссылается "
                        "на отсутствующую позицию заказа."
                    )

                issued_at = codec.read_text(record, "issued_at")
                issued_datetime = datetime.fromisoformat(issued_at)

                if issued_datetime.tzinfo is None:
                    raise ValueError(
                        "Дата выдачи доступа должна содержать часовой пояс."
                    )

                license_record = PurchaseLicense(
                    license_id,
                    order,
                    item,
                )
                license_record.issued_at = issued_at

                order.customer.add_purchased_book(item.book)
                store._licenses[license_id] = license_record
                licensed_items.add(item_key)

            for order in store._orders.values():
                if order.status == "paid":
                    for item in order.get_items():
                        if (order.id, item.book.id) not in licensed_items:
                            raise ValueError(
                                "Для оплаченной книги "
                                "отсутствует право доступа."
                            )

            restored_carts: set[int] = set()

            for record in codec.read_records(data, "carts"):
                customer_id = codec.read_id(record, "customer_id")

                if customer_id in restored_carts:
                    raise ValueError(
                        "Повторяющаяся корзина покупателя."
                    )

                cart = store.get_cart(customer_id)

                for book_id in cls.read_book_ids(record):
                    cart.add_book(store.catalog.get_book(book_id))

                restored_carts.add(customer_id)

            if restored_carts != set(store._customers):
                raise ValueError(
                    "Для каждого покупателя должна быть сохранена корзина."
                )

            store._next_order_id = max(
                store._orders,
                default=0,
            ) + 1
            store._next_payment_id = max(
                payment_ids,
                default=0,
            ) + 1
            store._next_license_id = max(
                store._licenses,
                default=0,
            ) + 1

            return store

        except (
            KeyError,
            TypeError,
            ValueError,
            DecimalException,
            BookStoreError,
        ) as error:
            raise BookStoreError(
                f"Некорректные данные магазина: {error}"
            ) from error


class JsonStoreStorage:
    """Сохранение и загрузка всего магазина в JSON."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def save(self, store: BookStore) -> None:
        """Проверить состояние и сохранить через временный файл."""
        data = StoreCodec.to_dict(store)
        StoreCodec.from_dict(data)

        text = json.dumps(data, ensure_ascii=False, indent=4)
        temporary_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(text, encoding="utf-8")
            temporary_path.replace(self.file_path)
        except OSError as error:
            raise BookStoreError(
                f"Не удалось сохранить магазин: {error}"
            ) from error

    def load(self) -> BookStore:
        """Прочитать JSON и восстановить проверенный магазин."""
        try:
            text = self.file_path.read_text(encoding="utf-8")
            data = json.loads(text)
        except FileNotFoundError as error:
            raise BookStoreError("Файл магазина не найден.") from error
        except (json.JSONDecodeError, UnicodeError) as error:
            raise BookStoreError(
                "Файл не является корректным JSON в кодировке UTF-8."
            ) from error
        except OSError as error:
            raise BookStoreError(
                f"Не удалось прочитать магазин: {error}"
            ) from error

        return StoreCodec.from_dict(data)
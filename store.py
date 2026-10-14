from cart import Cart
from catalog_service import BookCatalog
from customers import Customer
from errors import BookStoreError
from orders import Order
from purchases import Payment, PurchaseLicense


class BookStore:
    """Управление каталогом, покупателями и процессом покупки."""

    def __init__(self) -> None:
        self.catalog = BookCatalog()
        self._customers: dict[int, Customer] = {}
        self._carts: dict[int, Cart] = {}
        self._orders: dict[int, Order] = {}
        self._payments: dict[int, Payment] = {}
        self._licenses: dict[int, PurchaseLicense] = {}

        self._next_order_id = 1
        self._next_payment_id = 1
        self._next_license_id = 1

    def add_customer(self, customer: Customer) -> None:
        """Зарегистрировать покупателя и создать его корзину."""
        if customer.id in self._customers:
            raise BookStoreError(
                f"Покупатель с идентификатором {customer.id} уже существует."
            )

        self._customers[customer.id] = customer
        self._carts[customer.id] = Cart(customer)

    def get_customer(self, customer_id: int) -> Customer:
        """Получить зарегистрированного покупателя."""
        if customer_id not in self._customers:
            raise BookStoreError(
                f"Покупатель с идентификатором {customer_id} не найден."
            )

        return self._customers[customer_id]

    def get_cart(self, customer_id: int) -> Cart:
        """Получить корзину покупателя."""
        self.get_customer(customer_id)
        return self._carts[customer_id]

    def create_order(self, customer_id: int) -> Order:
        """Создать заказ и очистить корзину после успешного создания."""
        cart = self.get_cart(customer_id)
        order = Order(self._next_order_id, cart)

        self._orders[order.id] = order
        self._next_order_id += 1
        cart.clear()

        return order

    def get_order(self, order_id: int) -> Order:
        """Получить заказ по идентификатору."""
        if order_id not in self._orders:
            raise BookStoreError(
                f"Заказ с идентификатором {order_id} не найден."
            )

        return self._orders[order_id]

    def list_orders(self, customer_id: int) -> list[Order]:
        """Получить заказы указанного покупателя."""
        customer = self.get_customer(customer_id)

        return [
            order
            for order in self._orders.values()
            if order.customer is customer
        ]

    def pay_order(self, order_id: int, success: bool = True) -> bool:
        """Имитировать оплату и выдать доступ после её успеха."""
        order = self.get_order(order_id)

        if order.status != "created":
            raise BookStoreError(
                "Оплатить можно только созданный заказ."
            )

        items = order.get_items()

        for item in items:
            if order.customer.has_book(item.book.id):
                raise BookStoreError(
                    f"Книга «{item.book_title}» уже приобретена."
                )

        payment = self._payments.get(order_id)

        if payment is None:
            payment = Payment(self._next_payment_id, order)
            self._payments[order_id] = payment
            self._next_payment_id += 1

        if not payment.process(success):
            return False

        for item in items:
            license_record = PurchaseLicense(
                self._next_license_id,
                order,
                item,
            )
            self._licenses[license_record.id] = license_record
            self._next_license_id += 1
            order.customer.add_purchased_book(item.book)

        return True

    def cancel_order(self, order_id: int) -> None:
        """Отменить неоплаченный заказ."""
        self.get_order(order_id).cancel()

    def get_licenses(
        self,
        customer_id: int,
    ) -> list[PurchaseLicense]:
        """Получить права доступа указанного покупателя."""
        customer = self.get_customer(customer_id)

        return [
            license_record
            for license_record in self._licenses.values()
            if license_record.customer is customer
        ]
from decimal import Decimal

from cart import Cart
from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError
from orders import Order
from purchases import Payment, PurchaseLicense


def main() -> None:
    customer = Customer(1, "Анна", "anna@example.com")
    author = Author(1, "Александр Пушкин")
    publisher = Publisher(1, "Учебное издательство")
    category = Category(1, "Классика")

    first_book = DigitalBook(
        book_id=1,
        title="Капитанская дочка",
        author=author,
        publisher=publisher,
        category=category,
        price=Decimal("199.90"),
        file_format="EPUB",
        file_path="books/captains_daughter.epub",
    )

    second_book = DigitalBook(
        book_id=2,
        title="Евгений Онегин",
        author=author,
        publisher=publisher,
        category=category,
        price=Decimal("249.00"),
        file_format="PDF",
        file_path="books/eugene_onegin.pdf",
    )

    cart = Cart(customer)
    cart.add_book(first_book)
    cart.add_book(second_book)

    order = Order(1, cart)
    items = order.get_items()

    print(f"Заказ № {order.id}")
    print(f"Сумма: {order.get_total():.2f} руб.")
    print(f"Начальный статус: {order.status}")

    try:
        PurchaseLicense(1, order, items[0])
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    payment = Payment(1, order)

    result = payment.process(success=False)
    print(f"\nПервая попытка оплаты: {result}")
    print(f"Статус платежа: {payment.status}")
    print(f"Статус заказа: {order.status}")

    result = payment.process(success=True)
    print(f"\nВторая попытка оплаты: {result}")
    print(f"Статус платежа: {payment.status}")
    print(f"Статус заказа: {order.status}")

    licenses: list[PurchaseLicense] = []

    for license_id, item in enumerate(items, start=1):
        license_record = PurchaseLicense(license_id, order, item)
        licenses.append(license_record)
        customer.add_purchased_book(item.book)

    cart.clear()

    print("\nВыданные права доступа:")
    for license_record in licenses:
        print(
            f"{license_record.item.book_title} — "
            f"{license_record.get_file_path()}"
        )

    print(
        f"\nКниг у покупателя: "
        f"{len(customer.get_purchased_books())}"
    )
    print(f"Позиций в корзине: {len(cart.get_items())}")

    try:
        payment.process()
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    try:
        order.cancel()
    except BookStoreError as error:
        print(f"Ошибка обработана: {error}")


if __name__ == "__main__":
    main()
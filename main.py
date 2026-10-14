from decimal import Decimal

from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError
from store import BookStore


def main() -> None:
    store = BookStore()
    customer = Customer(1, "Анна", "anna@example.com")
    store.add_customer(customer)

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

    store.catalog.add_book(first_book)
    store.catalog.add_book(second_book)

    cart = store.get_cart(customer.id)
    cart.add_book(store.catalog.get_book(1))
    cart.add_book(store.catalog.get_book(2))

    order = store.create_order(customer.id)

    print(f"Создан заказ № {order.id}")
    print(f"Сумма заказа: {order.get_total():.2f} руб.")
    print(f"Позиций в корзине: {len(cart.get_items())}")

    # Второй заказ с той же книгой создан до оплаты первого.
    cart.add_book(first_book)
    second_order = store.create_order(customer.id)
    print(f"Создан второй заказ № {second_order.id}")

    result = store.pay_order(order.id, success=False)
    print(f"\nНеуспешная попытка оплаты: {result}")
    print(f"Статус первого заказа: {order.status}")
    print(f"Прав доступа: {len(store.get_licenses(customer.id))}")

    result = store.pay_order(order.id, success=True)
    print(f"\nУспешная попытка оплаты: {result}")
    print(f"Статус первого заказа: {order.status}")
    print(f"Книг у покупателя: {len(customer.get_purchased_books())}")
    print(f"Прав доступа: {len(store.get_licenses(customer.id))}")

    print("\nДоступные книги:")
    for license_record in store.get_licenses(customer.id):
        print(
            f"{license_record.item.book_title} — "
            f"{license_record.get_file_path()}"
        )

    try:
        store.pay_order(second_order.id)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    print(f"Статус второго заказа: {second_order.status}")
    print(f"Прав доступа после ошибки: {len(store.get_licenses(customer.id))}")

    store.cancel_order(second_order.id)
    print(f"Статус второго заказа после отмены: {second_order.status}")

    try:
        store.create_order(customer.id)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    print(f"Всего заказов покупателя: {len(store.list_orders(customer.id))}")


if __name__ == "__main__":
    main()
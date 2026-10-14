from decimal import Decimal

from cart import Cart
from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError
from orders import Order


def show_order(order: Order) -> None:
    """Вывести сведения о заказе."""
    print(f"Заказ № {order.id}")
    print(f"Покупатель: {order.customer.name}")
    print(f"Статус: {order.status}")

    for item in order.get_items():
        print(
            f"{item.book_title} — "
            f"{item.purchase_price:.2f} руб."
        )

    print(f"Сумма заказа: {order.get_total():.2f} руб.")


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

    print("Созданный заказ:")
    show_order(order)

    first_book.update("Капитанская дочка", Decimal("149.90"))

    print("\nПосле изменения цены в каталоге:")
    print(f"Цена первой книги: {first_book.price:.2f} руб.")
    print(f"Сумма корзины: {cart.get_total():.2f} руб.")
    print(f"Сумма заказа: {order.get_total():.2f} руб.")

    order.cancel()
    print(f"\nСтатус после отмены: {order.status}")

    try:
        order.cancel()
    except BookStoreError as error:
        print(f"Ошибка обработана: {error}")

    empty_cart = Cart(customer)

    try:
        Order(2, empty_cart)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")


if __name__ == "__main__":
    main()
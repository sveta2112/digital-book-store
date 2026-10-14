from decimal import Decimal

from cart import Cart
from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError


def show_cart(cart: Cart) -> None:
    """Вывести содержимое и стоимость корзины."""
    items = cart.get_items()

    if not items:
        print("Корзина пуста.")
    else:
        for item in items:
            print(
                f"{item.book.title} — "
                f"{item.get_price():.2f} руб."
            )

    print(f"Итого: {cart.get_total():.2f} руб.")


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
    print(f"Покупатель: {cart.customer.name}")

    print("\nНачальное состояние:")
    show_cart(cart)

    cart.add_book(first_book)
    cart.add_book(second_book)
    print("\nПосле добавления двух книг:")
    show_cart(cart)

    try:
        cart.add_book(first_book)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    first_book.update("Капитанская дочка", Decimal("149.90"))
    print("\nПосле изменения цены первой книги:")
    show_cart(cart)

    cart.remove_book(second_book.id)
    print("\nПосле удаления второй книги:")
    show_cart(cart)

    try:
        cart.remove_book(second_book.id)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    cart.clear()
    print("\nПосле очистки:")
    show_cart(cart)

    # Имитация ранее приобретённой книги для проверки ограничения.
    customer.add_purchased_book(second_book)

    try:
        cart.add_book(second_book)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")


if __name__ == "__main__":
    main()
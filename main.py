from decimal import Decimal

from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError


def main() -> None:
    customer = Customer(
        user_id=1,
        name="Анна",
        email="anna@example.com",
    )

    print(f"Покупатель: {customer.name}")
    print(f"Почта: {customer.email}")
    print(f"Приобретённых книг: {len(customer.get_purchased_books())}")

    customer.update_profile("Анна Иванова", "anna@example.com")
    print(f"После изменения имя: {customer.name}")

    try:
        customer.update_profile("Другое имя", "неверный адрес")
    except ValueError as error:
        print(f"Ошибка обработана: {error}")

    print(f"После ошибки имя сохранено: {customer.name}")
    print(f"После ошибки почта сохранена: {customer.email}")

    author = Author(1, "Александр Пушкин")
    publisher = Publisher(1, "Учебное издательство")
    category = Category(1, "Классика")

    book = DigitalBook(
        book_id=1,
        title="Капитанская дочка",
        author=author,
        publisher=publisher,
        category=category,
        price=Decimal("199.90"),
        file_format="EPUB",
        file_path="books/captains_daughter.epub",
    )

    print(f"Книга уже приобретена: {customer.has_book(book.id)}")

    # Проверка учёта книг без оформления заказа и оплаты.
    customer.add_purchased_book(book)

    print(f"После записи в коллекцию: {customer.has_book(book.id)}")
    print("Книги покупателя:")
    for purchased_book in customer.get_purchased_books():
        print(purchased_book.title)

    try:
        customer.add_purchased_book(book)
    except BookStoreError as error:
        print(f"Ошибка обработана: {error}")


if __name__ == "__main__":
    main()
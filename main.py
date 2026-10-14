from decimal import Decimal

from catalog import Author, Category, DigitalBook, Publisher
from console_app import ConsoleApp
from customers import Customer
from store import BookStore


def create_demo_store() -> BookStore:
    """Создать магазин с начальным каталогом и покупателем."""
    store = BookStore()
    store.add_customer(
        Customer(1, "Анна", "anna@example.com")
    )

    author = Author(1, "Александр Пушкин")
    publisher = Publisher(1, "Учебное издательство")
    category = Category(1, "Классика")

    store.catalog.add_book(
        DigitalBook(
            book_id=1,
            title="Капитанская дочка",
            author=author,
            publisher=publisher,
            category=category,
            price=Decimal("199.90"),
            file_format="EPUB",
            file_path="books/captains_daughter.epub",
        )
    )

    store.catalog.add_book(
        DigitalBook(
            book_id=2,
            title="Евгений Онегин",
            author=author,
            publisher=publisher,
            category=category,
            price=Decimal("249.00"),
            file_format="PDF",
            file_path="books/eugene_onegin.pdf",
        )
    )

    return store


def main() -> None:
    store = create_demo_store()
    app = ConsoleApp(store, customer_id=1)
    app.run()


if __name__ == "__main__":
    main()
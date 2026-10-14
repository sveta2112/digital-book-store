from decimal import Decimal
from pathlib import Path

from catalog import Author, Category, DigitalBook, Publisher
from customers import Customer
from errors import BookStoreError
from saved_console import SavedConsoleApp
from store import BookStore
from store_storage import JsonStoreStorage


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
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "shop_state.json"
    )
    storage = JsonStoreStorage(file_path)

    try:
        if file_path.exists():
            store = storage.load()
            store.get_customer(1)
            print("Загружено сохранённое состояние магазина.")
        else:
            store = create_demo_store()
            print("Создан начальный каталог магазина.")

    except BookStoreError as error:
        print(f"Не удалось открыть магазин: {error}")
        print(
            "Проверьте файл data/shop_state.json. "
            "Существующее сохранение не изменено."
        )
        raise SystemExit(1) from error

    app = SavedConsoleApp(
        store=store,
        customer_id=1,
        storage=storage,
    )
    app.run()


if __name__ == "__main__":
    main()
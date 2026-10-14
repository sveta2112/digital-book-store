from decimal import Decimal
from pathlib import Path

from catalog_storage import JsonCatalogStorage
from errors import BookStoreError
from main import create_demo_store


def main() -> None:
    try:
        store = create_demo_store()
        file_path = (
            Path(__file__).resolve().parent
            / "data"
            / "catalog.json"
        )
        storage = JsonCatalogStorage(file_path)

        storage.save(store.catalog)
        print("Каталог сохранён в data/catalog.json.")

        store.catalog.update_book(
            1,
            "Капитанская дочка",
            Decimal("50.00"),
        )
        store.catalog.remove_book(2)

        print("\nКаталог в памяти после изменений:")
        for book in store.catalog.list_books():
            print(f"{book.title} — {book.price:.2f} руб.")

        restored_catalog = storage.load()

        print("\nКаталог, восстановленный из JSON:")
        for book in restored_catalog.list_books():
            print(f"{book.title} — {book.price:.2f} руб.")

        first_book = restored_catalog.get_book(1)
        second_book = restored_catalog.get_book(2)

        print(
            "\nАвтор у двух книг — один объект:",
            first_book.author is second_book.author,
        )

        assert len(restored_catalog.list_books()) == 2
        assert first_book.price == Decimal("199.90")
        assert second_book.price == Decimal("249.00")
        assert first_book.author is second_book.author

        print("Проверки восстановления пройдены.")

    except BookStoreError as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
from decimal import Decimal

from catalog import Author, Category, DigitalBook, Publisher
from catalog_service import BookCatalog
from errors import BookStoreError


def show_catalog(catalog: BookCatalog) -> None:
    """Вывести книги из каталога."""
    books = catalog.list_books()
    if not books:
        print("Каталог пуст.")
        return

    for book in books:
        print(
            f"{book.id}. {book.title} — "
            f"{book.author.name}, {book.price:.2f} руб."
        )


def main() -> None:
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

    catalog = BookCatalog()
    catalog.add_book(first_book)
    catalog.add_book(second_book)

    print("Каталог после добавления:")
    show_catalog(catalog)

    print("\nПоиск по слову «КАПИТАН»:")
    for book in catalog.find_books("КАПИТАН"):
        print(book.title)

    catalog.update_book(
        book_id=1,
        title="Капитанская дочка",
        price=Decimal("149.90"),
    )
    print("\nКаталог после изменения цены:")
    show_catalog(catalog)

    try:
        catalog.add_book(first_book)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")

    catalog.remove_book(2)
    print("\nКаталог после удаления второй книги:")
    show_catalog(catalog)

    try:
        catalog.get_book(2)
    except BookStoreError as error:
        print(f"\nОшибка обработана: {error}")


if __name__ == "__main__":
    main()
from decimal import Decimal

from catalog import Author, Category, DigitalBook, Publisher


def main() -> None:
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
        file_format="epub",
        file_path="books/captains_daughter.epub",
    )

    print(f"Книга: {book.title}")
    print(f"Автор: {book.author.name}")
    print(f"Издательство: {book.publisher.name}")
    print(f"Категория: {book.category.name}")
    print(f"Формат: {book.file_format}")
    print(f"Цена: {book.price:.2f} руб.")

    book.update("Капитанская дочка", Decimal("149.90"))
    print(f"После изменения цена: {book.price:.2f} руб.")

    try:
        book.update("Капитанская дочка", Decimal("-10.00"))
    except ValueError as error:
        print(f"Ошибка обработана: {error}")

    print(f"После ошибки цена сохранена: {book.price:.2f} руб.")


if __name__ == "__main__":
    main()
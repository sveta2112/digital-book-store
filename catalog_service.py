from decimal import Decimal

from catalog import DigitalBook
from errors import BookStoreError


class BookCatalog:
    """Хранение книг и управление каталогом."""

    def __init__(self) -> None:
        self._books: dict[int, DigitalBook] = {}

    def add_book(self, book: DigitalBook) -> None:
        """Добавить книгу с уникальным идентификатором."""
        if book.id in self._books:
            raise BookStoreError(
                f"Книга с идентификатором {book.id} уже существует."
            )

        self._books[book.id] = book

    def get_book(self, book_id: int) -> DigitalBook:
        """Получить книгу по идентификатору."""
        if book_id not in self._books:
            raise BookStoreError(
                f"Книга с идентификатором {book_id} не найдена."
            )

        return self._books[book_id]

    def list_books(self) -> list[DigitalBook]:
        """Получить список книг в каталоге."""
        return list(self._books.values())

    def find_books(self, query: str) -> list[DigitalBook]:
        """Найти книги по части названия без учёта регистра."""
        query = query.strip().casefold()
        if not query:
            raise ValueError("Поисковый запрос не может быть пустым.")

        return [
            book
            for book in self._books.values()
            if query in book.title.casefold()
        ]

    def update_book(
        self,
        book_id: int,
        title: str,
        price: Decimal,
    ) -> None:
        """Изменить название и цену существующей книги."""
        book = self.get_book(book_id)
        book.update(title, price)

    def remove_book(self, book_id: int) -> None:
        """Удалить существующую книгу из каталога."""
        self.get_book(book_id)
        del self._books[book_id]
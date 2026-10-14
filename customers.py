from catalog import DigitalBook
from errors import BookStoreError


class User:
    """Пользователь магазина цифровых книг."""

    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
    ) -> None:
        if user_id <= 0:
            raise ValueError(
                "Идентификатор пользователя должен быть положительным."
            )

        self.id = user_id
        self.update_profile(name, email)

    def update_profile(self, name: str, email: str) -> None:
        """Изменить имя и электронную почту пользователя."""
        name = name.strip()
        email = email.strip()

        if not name:
            raise ValueError("Имя пользователя не может быть пустым.")

        if email.count("@") != 1:
            raise ValueError("Некорректный адрес электронной почты.")

        local_part, domain = email.split("@")
        if (
            not local_part
            or not domain
            or any(character.isspace() for character in email)
        ):
            raise ValueError("Некорректный адрес электронной почты.")

        self.name = name
        self.email = email


class Customer(User):
    """Покупатель с коллекцией приобретённых книг."""

    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
    ) -> None:
        super().__init__(user_id, name, email)
        self._purchased_books: dict[int, DigitalBook] = {}

    def has_book(self, book_id: int) -> bool:
        """Проверить, приобретена ли книга."""
        return book_id in self._purchased_books

    def get_purchased_books(self) -> list[DigitalBook]:
        """Получить список приобретённых книг."""
        return list(self._purchased_books.values())

    def add_purchased_book(self, book: DigitalBook) -> None:
        """Записать книгу в коллекцию после успешной покупки."""
        if self.has_book(book.id):
            raise BookStoreError(
                f"Книга «{book.title}» уже приобретена."
            )

        self._purchased_books[book.id] = book
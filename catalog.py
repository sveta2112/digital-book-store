from decimal import Decimal


class Author:
    """Автор цифровых книг."""

    def __init__(
        self,
        author_id: int,
        name: str,
        biography: str = "",
    ) -> None:
        if author_id <= 0:
            raise ValueError(
                "Идентификатор автора должен быть положительным."
            )

        name = name.strip()
        if not name:
            raise ValueError("Имя автора не может быть пустым.")

        self.id = author_id
        self.name = name
        self.biography = biography.strip()

    def update(self, name: str, biography: str) -> None:
        """Изменить имя и биографию автора."""
        name = name.strip()
        if not name:
            raise ValueError("Имя автора не может быть пустым.")

        self.name = name
        self.biography = biography.strip()


class Publisher:
    """Издательство цифровых книг."""

    def __init__(self, publisher_id: int, name: str) -> None:
        if publisher_id <= 0:
            raise ValueError(
                "Идентификатор издательства должен быть положительным."
            )

        self.id = publisher_id
        self.update(name)

    def update(self, name: str) -> None:
        """Изменить название издательства."""
        name = name.strip()
        if not name:
            raise ValueError(
                "Название издательства не может быть пустым."
            )

        self.name = name


class Category:
    """Категория цифровых книг."""

    def __init__(self, category_id: int, name: str) -> None:
        if category_id <= 0:
            raise ValueError(
                "Идентификатор категории должен быть положительным."
            )

        self.id = category_id
        self.update(name)

    def update(self, name: str) -> None:
        """Изменить название категории."""
        name = name.strip()
        if not name:
            raise ValueError(
                "Название категории не может быть пустым."
            )

        self.name = name


class DigitalBook:
    """Цифровая книга в каталоге."""

    SUPPORTED_FORMATS = ("PDF", "EPUB", "FB2")

    def __init__(
        self,
        book_id: int,
        title: str,
        author: Author,
        publisher: Publisher,
        category: Category,
        price: Decimal,
        file_format: str,
        file_path: str,
    ) -> None:
        if book_id <= 0:
            raise ValueError(
                "Идентификатор книги должен быть положительным."
            )

        file_format = file_format.strip().upper()
        if file_format not in self.SUPPORTED_FORMATS:
            raise ValueError("Допустимые форматы книги: PDF, EPUB, FB2.")

        file_path = file_path.strip()
        if not file_path:
            raise ValueError("Путь к файлу книги не может быть пустым.")

        self.id = book_id
        self.author = author
        self.publisher = publisher
        self.category = category
        self.file_format = file_format
        self.file_path = file_path
        self.update(title, price)

    def update(self, title: str, price: Decimal) -> None:
        """Изменить название и цену книги."""
        title = title.strip()
        if not title:
            raise ValueError("Название книги не может быть пустым.")

        if not isinstance(price, Decimal):
            raise TypeError("Цена должна иметь тип Decimal.")

        if not price.is_finite() or price < 0:
            raise ValueError(
                "Цена должна быть конечным неотрицательным числом."
            )

        if price % Decimal("0.01") != 0:
            raise ValueError(
                "Цена не может содержать доли меньше одной копейки."
            )

        self.title = title
        self.price = price
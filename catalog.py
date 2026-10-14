class Author:
    """Автор цифровых книг."""

    def __init__(
        self,
        author_id: int,
        name: str,
        biography: str = "",
    ) -> None:
        if author_id <= 0:
            raise ValueError("Идентификатор автора должен быть положительным.")

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
            raise ValueError("Название издательства не может быть пустым.")

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
            raise ValueError("Название категории не может быть пустым.")

        self.name = name
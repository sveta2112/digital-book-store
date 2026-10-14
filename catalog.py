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
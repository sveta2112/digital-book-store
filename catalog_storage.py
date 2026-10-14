import json
from decimal import Decimal, DecimalException
from pathlib import Path
from typing import Any

from catalog import Author, Category, DigitalBook, Publisher
from catalog_service import BookCatalog
from errors import BookStoreError


class CatalogCodec:
    """Преобразование каталога в словарь и обратно."""

    @staticmethod
    def to_dict(catalog: BookCatalog) -> dict[str, Any]:
        """Подготовить структуру для хранения каталога."""
        books = catalog.list_books()
        authors = {book.author.id: book.author for book in books}
        publishers = {
            book.publisher.id: book.publisher for book in books
        }
        categories = {
            book.category.id: book.category for book in books
        }

        return {
            "version": 1,
            "authors": [
                {
                    "id": author.id,
                    "name": author.name,
                    "biography": author.biography,
                }
                for author in authors.values()
            ],
            "publishers": [
                {"id": publisher.id, "name": publisher.name}
                for publisher in publishers.values()
            ],
            "categories": [
                {"id": category.id, "name": category.name}
                for category in categories.values()
            ],
            "books": [
                {
                    "id": book.id,
                    "title": book.title,
                    "author_id": book.author.id,
                    "publisher_id": book.publisher.id,
                    "category_id": book.category.id,
                    "price": str(book.price),
                    "file_format": book.file_format,
                    "file_path": book.file_path,
                }
                for book in books
            ],
        }

    @staticmethod
    def read_id(record: dict[str, Any], key: str) -> int:
        """Проверить идентификатор из файла."""
        value = record[key]
        if type(value) is not int or value <= 0:
            raise ValueError(
                f"Поле «{key}» должно быть положительным целым числом."
            )
        return value

    @staticmethod
    def read_text(record: dict[str, Any], key: str) -> str:
        """Проверить строковое поле из файла."""
        value = record[key]
        if not isinstance(value, str):
            raise ValueError(f"Поле «{key}» должно быть строкой.")
        return value

    @staticmethod
    def read_records(
        data: dict[str, Any],
        key: str,
    ) -> list[dict[str, Any]]:
        """Проверить список записей."""
        records = data[key]
        if not isinstance(records, list):
            raise ValueError(f"Поле «{key}» должно быть списком.")

        if not all(isinstance(record, dict) for record in records):
            raise ValueError(
                f"Список «{key}» должен содержать объекты."
            )

        return records

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BookCatalog:
        """Восстановить каталог с проверкой структуры и связей."""
        try:
            if not isinstance(data, dict):
                raise ValueError("Корень документа должен быть объектом.")

            if type(data.get("version")) is not int:
                raise ValueError("Версия формата должна быть целым числом.")

            if data["version"] != 1:
                raise ValueError("Неподдерживаемая версия формата.")

            authors: dict[int, Author] = {}
            for record in cls.read_records(data, "authors"):
                author_id = cls.read_id(record, "id")
                if author_id in authors:
                    raise ValueError("Повторяющийся идентификатор автора.")

                authors[author_id] = Author(
                    author_id,
                    cls.read_text(record, "name"),
                    cls.read_text(record, "biography"),
                )

            publishers: dict[int, Publisher] = {}
            for record in cls.read_records(data, "publishers"):
                publisher_id = cls.read_id(record, "id")
                if publisher_id in publishers:
                    raise ValueError(
                        "Повторяющийся идентификатор издательства."
                    )

                publishers[publisher_id] = Publisher(
                    publisher_id,
                    cls.read_text(record, "name"),
                )

            categories: dict[int, Category] = {}
            for record in cls.read_records(data, "categories"):
                category_id = cls.read_id(record, "id")
                if category_id in categories:
                    raise ValueError(
                        "Повторяющийся идентификатор категории."
                    )

                categories[category_id] = Category(
                    category_id,
                    cls.read_text(record, "name"),
                )

            catalog = BookCatalog()

            for record in cls.read_records(data, "books"):
                book = DigitalBook(
                    book_id=cls.read_id(record, "id"),
                    title=cls.read_text(record, "title"),
                    author=authors[cls.read_id(record, "author_id")],
                    publisher=publishers[
                        cls.read_id(record, "publisher_id")
                    ],
                    category=categories[
                        cls.read_id(record, "category_id")
                    ],
                    price=Decimal(cls.read_text(record, "price")),
                    file_format=cls.read_text(record, "file_format"),
                    file_path=cls.read_text(record, "file_path"),
                )
                catalog.add_book(book)

            return catalog

        except (
            KeyError,
            TypeError,
            ValueError,
            DecimalException,
            BookStoreError,
        ) as error:
            raise BookStoreError(
                f"Некорректная структура каталога: {error}"
            ) from error


class JsonCatalogStorage:
    """Сохранение и загрузка каталога в формате JSON."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def save(self, catalog: BookCatalog) -> None:
        """Сохранить каталог в UTF-8 через временный файл."""
        data = CatalogCodec.to_dict(catalog)
        text = json.dumps(data, ensure_ascii=False, indent=4)
        temporary_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(text, encoding="utf-8")
            temporary_path.replace(self.file_path)
        except OSError as error:
            raise BookStoreError(
                f"Не удалось сохранить каталог: {error}"
            ) from error

    def load(self) -> BookCatalog:
        """Прочитать JSON и восстановить каталог."""
        try:
            text = self.file_path.read_text(encoding="utf-8")
            data = json.loads(text)
        except FileNotFoundError as error:
            raise BookStoreError("Файл каталога не найден.") from error
        except (json.JSONDecodeError, UnicodeError) as error:
            raise BookStoreError(
                "Файл не является корректным JSON в кодировке UTF-8."
            ) from error
        except OSError as error:
            raise BookStoreError(
                f"Не удалось прочитать каталог: {error}"
            ) from error

        return CatalogCodec.from_dict(data)
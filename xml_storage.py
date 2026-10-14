import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from errors import BookStoreError
from store import BookStore
from store_storage import StoreCodec


class XmlStoreStorage:
    """Сохранение и загрузка магазина в XML."""

    ITEM_TAGS = {
        "authors": "author",
        "publishers": "publisher",
        "categories": "category",
        "books": "book",
        "customers": "customer",
        "carts": "cart",
        "orders": "order",
        "payments": "payment",
        "licenses": "license",
        "items": "order_item",
        "book_ids": "book_id",
    }

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    @classmethod
    def encode_element(cls, element: ET.Element, value: Any) -> None:
        """Записать значение в XML с указанием его типа."""
        if isinstance(value, dict):
            element.set("type", "object")

            for key, child_value in value.items():
                child = ET.SubElement(element, key)
                cls.encode_element(child, child_value)

        elif isinstance(value, list):
            element.set("type", "array")
            item_tag = cls.ITEM_TAGS.get(element.tag, "item")

            for child_value in value:
                child = ET.SubElement(element, item_tag)
                cls.encode_element(child, child_value)

        elif type(value) is int:
            element.set("type", "integer")
            element.text = str(value)

        elif isinstance(value, str):
            element.set("type", "string")
            element.text = value

        else:
            raise ValueError("Неподдерживаемый тип данных для XML.")

    @classmethod
    def decode_element(cls, element: ET.Element) -> Any:
        """Восстановить значение из XML с проверкой структуры."""
        if set(element.attrib) != {"type"}:
            raise ValueError(
                f"Некорректные атрибуты элемента «{element.tag}»."
            )

        value_type = element.attrib["type"]
        children = list(element)

        if value_type in ("object", "array"):
            if (element.text or "").strip():
                raise ValueError(
                    "Объект или список не должен содержать обычный текст."
                )

            if any((child.tail or "").strip() for child in children):
                raise ValueError("Обнаружен текст между элементами XML.")

        if value_type == "object":
            result: dict[str, Any] = {}

            for child in children:
                if child.tag in result:
                    raise ValueError(
                        f"Повторяющееся поле «{child.tag}»."
                    )

                result[child.tag] = cls.decode_element(child)

            return result

        if value_type == "array":
            item_tag = cls.ITEM_TAGS.get(element.tag, "item")

            if any(child.tag != item_tag for child in children):
                raise ValueError(
                    f"Некорректный элемент списка «{element.tag}»."
                )

            return [
                cls.decode_element(child)
                for child in children
            ]

        if children:
            raise ValueError(
                "Строка или число не должны содержать вложенные элементы."
            )

        if value_type == "integer":
            return int(element.text or "")

        if value_type == "string":
            return element.text or ""

        raise ValueError(f"Неизвестный тип XML: {value_type}.")

    def save(self, store: BookStore) -> None:
        """Проверить данные и сохранить XML через временный файл."""
        data = StoreCodec.to_dict(store)
        StoreCodec.from_dict(data)

        temporary_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        try:
            root = ET.Element("book_store")
            self.encode_element(root, data)
            ET.indent(root, space="    ")

            content = ET.tostring(
                root,
                encoding="utf-8",
                xml_declaration=True,
            )

            # Проверка, что сформированный документ можно прочитать.
            ET.fromstring(content)

            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_bytes(content)
            temporary_path.replace(self.file_path)

        except (
            OSError,
            ValueError,
            TypeError,
            UnicodeError,
            ET.ParseError,
        ) as error:
            raise BookStoreError(
                f"Не удалось сохранить XML: {error}"
            ) from error

    def load(self) -> BookStore:
        """Прочитать XML и восстановить новый магазин."""
        try:
            content = self.file_path.read_bytes()
            root = ET.fromstring(content)

            if root.tag != "book_store":
                raise ValueError("Корневой элемент должен быть book_store.")

            data = self.decode_element(root)

        except FileNotFoundError as error:
            raise BookStoreError("Файл XML не найден.") from error
        except (ET.ParseError, ValueError, UnicodeError) as error:
            raise BookStoreError(
                f"Некорректный документ XML: {error}"
            ) from error
        except OSError as error:
            raise BookStoreError(
                f"Не удалось прочитать XML: {error}"
            ) from error

        return StoreCodec.from_dict(data)
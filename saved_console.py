from decimal import DecimalException
from typing import Callable

from console_app import ConsoleApp
from errors import BookStoreError
from store import BookStore
from store_storage import JsonStoreStorage
from xml_storage import XmlStoreStorage


class SavedConsoleApp(ConsoleApp):
    """Меню магазина с сохранением JSON и обменом данными XML."""

    def __init__(
        self,
        store: BookStore,
        customer_id: int,
        storage: JsonStoreStorage,
    ) -> None:
        super().__init__(store, customer_id)
        self.storage = storage
        self.xml_storage = XmlStoreStorage(
            storage.file_path.with_suffix(".xml")
        )

    def get_actions(
        self,
    ) -> dict[str, tuple[str, Callable[[], None]]]:
        """Связать номера меню, подписи и действия."""
        return {
            "1": ("Показать каталог", self.show_catalog),
            "2": ("Найти книгу", self.find_books),
            "3": ("Добавить книгу в корзину", self.add_to_cart),
            "4": ("Показать корзину", self.show_cart),
            "5": ("Удалить книгу из корзины", self.remove_from_cart),
            "6": ("Очистить корзину", self.clear_cart),
            "7": ("Оформить заказ", self.create_order),
            "8": ("Показать мои заказы", self.show_orders),
            "9": (
                "Оплатить заказ — учебная имитация",
                self.pay_order,
            ),
            "10": ("Отменить заказ", self.cancel_order),
            "11": (
                "Показать приобретённые книги",
                self.show_purchased_books,
            ),
            "12": (
                "Добавить книгу в каталог",
                self.add_catalog_book,
            ),
            "13": (
                "Изменить название и цену книги",
                self.update_catalog_book,
            ),
            "14": (
                "Удалить книгу из каталога",
                self.remove_catalog_book,
            ),
            "15": ("Сохранить данные в JSON", self.save_data),
            "16": ("Загрузить сохранение JSON", self.load_data),
            "17": ("Экспортировать магазин в XML", self.export_xml),
            "18": ("Загрузить магазин из XML", self.import_xml),
        }

    def show_menu(self) -> None:
        """Вывести доступные действия."""
        print("\nМагазин цифровых книг")

        for number, (description, _) in self.get_actions().items():
            print(f"{number}. {description}")

        print("0. Сохранить данные в JSON и выйти")

    def save_data(self) -> None:
        """Сохранить текущее состояние в JSON."""
        self.storage.save(self.store)
        print("Данные магазина сохранены в JSON.")

    def load_from(
        self,
        storage: JsonStoreStorage | XmlStoreStorage,
    ) -> None:
        """Заменить состояние только после успешной загрузки."""
        answer = input(
            "Несохранённые изменения будут заменены. "
            "Для загрузки введите «да»: "
        ).strip().casefold()

        if answer != "да":
            print("Загрузка отменена.")
            return

        restored_store = storage.load()
        restored_store.get_customer(self.customer_id)

        self.store = restored_store
        print("Сохранённые данные магазина загружены.")

    def load_data(self) -> None:
        """Загрузить последнее сохранение JSON."""
        self.load_from(self.storage)

    def export_xml(self) -> None:
        """Сохранить текущее состояние в XML."""
        self.xml_storage.save(self.store)
        print("Магазин экспортирован в XML.")

    def import_xml(self) -> None:
        """Загрузить состояние из XML."""
        self.load_from(self.xml_storage)

    def run(self) -> None:
        """Обрабатывать команды и сохранять JSON при выходе."""
        print(
            "При выходе через пункт 0 данные сохраняются в JSON."
        )
        print(
            "Для обмена данными в XML используйте пункты 17 и 18."
        )

        while True:
            try:
                self.show_menu()
                choice = input("Выберите действие: ").strip()

                if choice == "0":
                    self.save_data()
                    print("Работа завершена.")
                    return

                action_entry = self.get_actions().get(choice)
                if action_entry is None:
                    print("Неизвестная команда. Выберите пункт меню.")
                    continue

                _, action = action_entry
                action()

            except BookStoreError as error:
                print(f"Операция не выполнена: {error}")
            except DecimalException:
                print("Ошибка ввода: некорректное значение цены.")
            except ValueError as error:
                print(f"Ошибка ввода: {error}")
            except (EOFError, KeyboardInterrupt):
                try:
                    self.save_data()
                except BookStoreError as error:
                    print(f"\nНе удалось сохранить данные: {error}")
                    raise SystemExit(1) from error

                print("\nРабота завершена.")
                return
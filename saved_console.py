from decimal import DecimalException

from console_app import ConsoleApp
from errors import BookStoreError
from store import BookStore
from store_storage import JsonStoreStorage


class SavedConsoleApp(ConsoleApp):
    """Меню магазина с сохранением и загрузкой JSON."""

    def __init__(
        self,
        store: BookStore,
        customer_id: int,
        storage: JsonStoreStorage,
    ) -> None:
        super().__init__(store, customer_id)
        self.storage = storage

    def show_menu(self) -> None:
        """Вывести команды магазина и работы с сохранением."""
        print("\nМагазин цифровых книг")
        print("1. Показать каталог")
        print("2. Найти книгу")
        print("3. Добавить книгу в корзину")
        print("4. Показать корзину")
        print("5. Удалить книгу из корзины")
        print("6. Очистить корзину")
        print("7. Оформить заказ")
        print("8. Показать мои заказы")
        print("9. Оплатить заказ — учебная имитация")
        print("10. Отменить заказ")
        print("11. Показать приобретённые книги")
        print("12. Добавить книгу в каталог")
        print("13. Изменить название и цену книги")
        print("14. Удалить книгу из каталога")
        print("15. Сохранить данные")
        print("16. Загрузить последнее сохранение")
        print("0. Сохранить данные и выйти")

    def save_data(self) -> None:
        """Сохранить текущее состояние магазина."""
        self.storage.save(self.store)
        print("Данные магазина сохранены.")

    def load_data(self) -> None:
        """Заменить состояние после успешной проверки сохранения."""
        answer = input(
            "Несохранённые изменения будут заменены. "
            "Для загрузки введите «да»: "
        ).strip().casefold()

        if answer != "да":
            print("Загрузка отменена.")
            return

        restored_store = self.storage.load()
        restored_store.get_customer(self.customer_id)

        self.store = restored_store
        print("Сохранённые данные магазина загружены.")

    def run(self) -> None:
        """Обрабатывать команды и сохранять данные при выходе."""
        actions = {
            "1": self.show_catalog,
            "2": self.find_books,
            "3": self.add_to_cart,
            "4": self.show_cart,
            "5": self.remove_from_cart,
            "6": self.clear_cart,
            "7": self.create_order,
            "8": self.show_orders,
            "9": self.pay_order,
            "10": self.cancel_order,
            "11": self.show_purchased_books,
            "12": self.add_catalog_book,
            "13": self.update_catalog_book,
            "14": self.remove_catalog_book,
            "15": self.save_data,
            "16": self.load_data,
        }

        print(
            "При выходе через пункт 0 данные сохраняются автоматически."
        )
        print("Для сохранения во время работы выберите пункт 15.")

        while True:
            try:
                self.show_menu()
                choice = input("Выберите действие: ").strip()

                if choice == "0":
                    self.save_data()
                    print("Работа завершена.")
                    return

                action = actions.get(choice)
                if action is None:
                    print("Неизвестная команда. Выберите пункт меню.")
                    continue

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
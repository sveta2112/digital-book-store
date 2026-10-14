from errors import BookStoreError
from store import BookStore


class ConsoleApp:
    """Консольный интерфейс магазина для одного покупателя."""

    def __init__(self, store: BookStore, customer_id: int) -> None:
        self.store = store
        self.customer_id = customer_id
        self.store.get_customer(customer_id)

    def show_menu(self) -> None:
        """Вывести доступные команды."""
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
        print("0. Выйти")

    @staticmethod
    def read_id(prompt: str) -> int:
        """Прочитать положительный идентификатор."""
        value = int(input(prompt))
        if value <= 0:
            raise ValueError(
                "Идентификатор должен быть положительным."
            )
        return value

    def show_catalog(self) -> None:
        """Показать книги каталога."""
        books = self.store.catalog.list_books()
        if not books:
            print("Каталог пуст.")
            return

        for book in books:
            print(
                f"{book.id}. {book.title} — "
                f"{book.author.name}, "
                f"{book.price:.2f} руб., {book.file_format}"
            )

    def find_books(self) -> None:
        """Найти книги по части названия."""
        query = input("Введите часть названия: ")
        books = self.store.catalog.find_books(query)

        if not books:
            print("Книги не найдены.")
            return

        for book in books:
            print(
                f"{book.id}. {book.title} — "
                f"{book.price:.2f} руб."
            )

    def add_to_cart(self) -> None:
        """Добавить выбранную книгу в корзину."""
        book_id = self.read_id("Идентификатор книги: ")
        book = self.store.catalog.get_book(book_id)
        self.store.get_cart(self.customer_id).add_book(book)
        print(f"Книга «{book.title}» добавлена в корзину.")

    def show_cart(self) -> None:
        """Показать корзину и общую стоимость."""
        cart = self.store.get_cart(self.customer_id)
        items = cart.get_items()

        if not items:
            print("Корзина пуста.")
        else:
            for item in items:
                print(
                    f"{item.book.id}. {item.book.title} — "
                    f"{item.get_price():.2f} руб."
                )

        print(f"Итого: {cart.get_total():.2f} руб.")

    def remove_from_cart(self) -> None:
        """Удалить выбранную книгу из корзины."""
        book_id = self.read_id("Идентификатор книги: ")
        self.store.get_cart(self.customer_id).remove_book(book_id)
        print("Книга удалена из корзины.")

    def clear_cart(self) -> None:
        """Очистить корзину покупателя."""
        self.store.get_cart(self.customer_id).clear()
        print("Корзина очищена.")

    def create_order(self) -> None:
        """Оформить заказ из текущей корзины."""
        order = self.store.create_order(self.customer_id)
        print(
            f"Создан заказ № {order.id}. "
            f"Сумма: {order.get_total():.2f} руб."
        )
        print("Корзина очищена. Заказ ожидает оплаты.")

    def show_orders(self) -> None:
        """Показать заказы текущего покупателя."""
        orders = self.store.list_orders(self.customer_id)
        if not orders:
            print("Заказов пока нет.")
            return

        status_names = {
            "created": "ожидает оплаты",
            "paid": "оплачен",
            "cancelled": "отменён",
        }

        for order in orders:
            status = status_names.get(order.status, order.status)
            print(
                f"\nЗаказ № {order.id}: {status}, "
                f"{order.get_total():.2f} руб."
            )
            for item in order.get_items():
                print(
                    f"  {item.book_title} — "
                    f"{item.purchase_price:.2f} руб."
                )

    def read_own_order_id(self) -> int:
        """Прочитать идентификатор заказа текущего покупателя."""
        order_id = self.read_id("Номер заказа: ")
        order = self.store.get_order(order_id)
        customer = self.store.get_customer(self.customer_id)

        if order.customer is not customer:
            raise BookStoreError(
                "Этот заказ принадлежит другому покупателю."
            )

        return order_id

    def pay_order(self) -> None:
        """Выбрать результат учебной оплаты."""
        order_id = self.read_own_order_id()
        answer = input(
            "Результат учебной оплаты "
            "(1 — успех, 2 — отказ): "
        ).strip()

        if answer not in ("1", "2"):
            raise ValueError("Введите 1 или 2.")

        success = self.store.pay_order(
            order_id,
            success=answer == "1",
        )

        if success:
            print("Заказ оплачен. Доступ к книгам выдан.")
        else:
            print(
                "Оплата не прошла. "
                "Можно повторить попытку или отменить заказ."
            )

    def cancel_order(self) -> None:
        """Отменить заказ текущего покупателя."""
        order_id = self.read_own_order_id()
        self.store.cancel_order(order_id)
        print("Заказ отменён.")

    def show_purchased_books(self) -> None:
        """Показать приобретённые книги и записанные пути к файлам."""
        licenses = self.store.get_licenses(self.customer_id)
        if not licenses:
            print("Приобретённых книг пока нет.")
            return

        for license_record in licenses:
            print(
                f"{license_record.item.book_title} — "
                f"{license_record.get_file_path()}"
            )

    def run(self) -> None:
        """Обрабатывать команды до выхода пользователя."""
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
        }

        print(
            "Учебная версия: изменения сохраняются "
            "только до закрытия программы."
        )

        while True:
            try:
                self.show_menu()
                choice = input("Выберите действие: ").strip()

                if choice == "0":
                    print("Работа завершена.")
                    return

                action = actions.get(choice)
                if action is None:
                    print("Неизвестная команда. Выберите пункт меню.")
                    continue

                action()

            except BookStoreError as error:
                print(f"Операция не выполнена: {error}")
            except ValueError as error:
                print(f"Ошибка ввода: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nРабота завершена.")
                return
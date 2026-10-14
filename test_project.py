import copy
import io
import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cart import Cart
from errors import BookStoreError
from main import create_demo_store
from orders import Order
from saved_console import SavedConsoleApp
from store import BookStore
from store_storage import JsonStoreStorage, StoreCodec
from xml_storage import XmlStoreStorage


class BookStoreTests(unittest.TestCase):
    """Проверки покупки, хранения данных и обработки ошибок."""

    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.store = create_demo_store()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def make_saved_store() -> BookStore:
        """Создать состояние с покупкой, отменой и корзиной."""
        store = create_demo_store()
        cart = store.get_cart(1)

        cart.add_book(store.catalog.get_book(1))
        first_order = store.create_order(1)
        store.pay_order(first_order.id)

        cart.add_book(store.catalog.get_book(2))
        second_order = store.create_order(1)
        store.pay_order(second_order.id, success=False)
        store.cancel_order(second_order.id)

        cart.add_book(store.catalog.get_book(2))
        store.catalog.update_book(
            1,
            "Капитанская дочка — новая редакция",
            Decimal("50.00"),
        )

        return store

    def test_invalid_book_update_preserves_data(self) -> None:
        book = self.store.catalog.get_book(1)
        original_title = book.title
        original_price = book.price

        for price in (
            Decimal("-1.00"),
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("0.001"),
        ):
            with self.subTest(price=str(price)):
                with self.assertRaises(ValueError):
                    book.update("Другое название", price)

                self.assertEqual(book.title, original_title)
                self.assertEqual(book.price, original_price)

    def test_cart_total_and_duplicate(self) -> None:
        cart = self.store.get_cart(1)
        first_book = self.store.catalog.get_book(1)
        second_book = self.store.catalog.get_book(2)

        self.assertEqual(cart.get_total(), Decimal("0.00"))

        cart.add_book(first_book)
        cart.add_book(second_book)
        self.assertEqual(cart.get_total(), Decimal("448.90"))

        with self.assertRaises(BookStoreError):
            cart.add_book(first_book)

        first_book.update(first_book.title, Decimal("149.90"))
        self.assertEqual(cart.get_total(), Decimal("398.90"))

        cart.clear()
        self.assertEqual(cart.get_total(), Decimal("0.00"))

    def test_order_keeps_original_title_and_price(self) -> None:
        book = self.store.catalog.get_book(1)
        cart = self.store.get_cart(1)
        cart.add_book(book)
        order = self.store.create_order(1)

        book.update("Новое название", Decimal("50.00"))

        self.assertEqual(
            order.get_items()[0].book_title,
            "Капитанская дочка",
        )
        self.assertEqual(order.get_total(), Decimal("199.90"))
        self.assertEqual(len(cart.get_items()), 0)

        order.cancel()
        with self.assertRaises(BookStoreError):
            order.cancel()

        with self.assertRaises(BookStoreError):
            Order(2, Cart(self.store.get_customer(1)))

    def test_failed_payment_can_be_retried(self) -> None:
        cart = self.store.get_cart(1)
        cart.add_book(self.store.catalog.get_book(1))
        order = self.store.create_order(1)

        self.assertFalse(
            self.store.pay_order(order.id, success=False)
        )
        self.assertEqual(order.status, "created")
        self.assertEqual(len(self.store.get_licenses(1)), 0)
        self.assertFalse(self.store.get_customer(1).has_book(1))

        self.assertTrue(self.store.pay_order(order.id))
        self.assertEqual(order.status, "paid")
        self.assertEqual(len(self.store.get_licenses(1)), 1)

        with self.assertRaises(BookStoreError):
            self.store.pay_order(order.id)

        with self.assertRaises(BookStoreError):
            self.store.cancel_order(order.id)

    def test_overlapping_orders_do_not_duplicate_purchase(self) -> None:
        cart = self.store.get_cart(1)
        book = self.store.catalog.get_book(1)

        cart.add_book(book)
        first_order = self.store.create_order(1)

        cart.add_book(book)
        second_order = self.store.create_order(1)

        self.store.pay_order(first_order.id)

        with self.assertRaises(BookStoreError):
            self.store.pay_order(second_order.id)

        self.assertEqual(second_order.status, "created")
        self.assertEqual(len(self.store.get_licenses(1)), 1)

    def test_json_and_xml_round_trip(self) -> None:
        adapters = (
            (JsonStoreStorage, "shop.json"),
            (XmlStoreStorage, "shop.xml"),
        )

        for adapter_class, filename in adapters:
            with self.subTest(format=filename):
                original = self.make_saved_store()
                storage = adapter_class(self.directory / filename)
                storage.save(original)
                restored = storage.load()

                self.assertEqual(
                    StoreCodec.to_dict(restored),
                    StoreCodec.to_dict(original),
                )
                self.assertIs(
                    restored.catalog.get_book(1).author,
                    restored.catalog.get_book(2).author,
                )
                self.assertEqual(
                    restored.get_order(1).get_total(),
                    Decimal("199.90"),
                )
                self.assertEqual(
                    restored.get_cart(1).get_total(),
                    Decimal("249.00"),
                )

                next_order = restored.create_order(1)
                self.assertEqual(next_order.id, 3)
                self.assertTrue(restored.pay_order(next_order.id))
                self.assertEqual(
                    len(restored.get_licenses(1)),
                    2,
                )

    def test_inconsistent_saved_data_is_rejected(self) -> None:
        original_data = StoreCodec.to_dict(self.make_saved_store())

        changes = (
            (
                "missing_license",
                lambda data: data["licenses"].clear(),
            ),
            (
                "wrong_payment_amount",
                lambda data: data["payments"][0].update(
                    amount="0.01"
                ),
            ),
            (
                "missing_book",
                lambda data: data["orders"][0]["items"][0].update(
                    book_id=999
                ),
            ),
            (
                "invalid_price",
                lambda data: data["catalog"]["books"][0].update(
                    price="NaN"
                ),
            ),
        )

        for name, change in changes:
            with self.subTest(case=name):
                data = copy.deepcopy(original_data)
                change(data)

                with self.assertRaises(BookStoreError):
                    StoreCodec.from_dict(data)

    def test_missing_and_malformed_files_are_rejected(self) -> None:
        adapters = (
            (JsonStoreStorage, "broken.json", '{"version":'),
            (XmlStoreStorage, "broken.xml", "<book_store"),
        )

        for adapter_class, filename, content in adapters:
            with self.subTest(format=filename):
                path = self.directory / filename
                storage = adapter_class(path)

                with self.assertRaises(BookStoreError):
                    storage.load()

                path.write_text(content, encoding="utf-8")

                with self.assertRaises(BookStoreError):
                    storage.load()

                self.assertEqual(
                    path.read_text(encoding="utf-8"),
                    content,
                )

    def test_duplicate_xml_fields_are_rejected(self) -> None:
        path = self.directory / "duplicate.xml"
        path.write_text(
            '<book_store type="object">'
            '<version type="integer">1</version>'
            '<version type="integer">1</version>'
            '</book_store>',
            encoding="utf-8",
        )

        with self.assertRaises(BookStoreError):
            XmlStoreStorage(path).load()

    def test_failed_loading_keeps_current_store(self) -> None:
        path = self.directory / "broken.json"
        path.write_text("{", encoding="utf-8")

        app = SavedConsoleApp(
            self.store,
            1,
            JsonStoreStorage(path),
        )

        with patch("builtins.input", return_value="да"):
            with self.assertRaises(BookStoreError):
                app.load_data()

        self.assertIs(app.store, self.store)

    def test_invalid_console_input_returns_to_menu(self) -> None:
        storage = JsonStoreStorage(self.directory / "shop.json")
        app = SavedConsoleApp(self.store, 1, storage)
        output = io.StringIO()

        with patch(
            "builtins.input",
            side_effect=["3", "abc", "0"],
        ):
            with patch("sys.stdout", output):
                app.run()

        self.assertIn("Ошибка ввода:", output.getvalue())
        self.assertIn("Работа завершена.", output.getvalue())
        self.assertEqual(
            len(storage.load().get_cart(1).get_items()),
            0,
        )

    def test_failed_exit_save_keeps_program_running(self) -> None:
        storage = JsonStoreStorage(self.directory / "shop.json")
        app = SavedConsoleApp(self.store, 1, storage)
        output = io.StringIO()

        with patch.object(
            storage,
            "save",
            side_effect=[
                BookStoreError("Проверочная ошибка сохранения."),
                None,
            ],
        ) as save_mock:
            with patch("builtins.input", side_effect=["0", "0"]):
                with patch("sys.stdout", output):
                    app.run()

        self.assertEqual(save_mock.call_count, 2)
        self.assertIn(
            "Операция не выполнена:",
            output.getvalue(),
        )
        self.assertIn("Работа завершена.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
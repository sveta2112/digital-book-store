from decimal import Decimal
from pathlib import Path

from errors import BookStoreError
from main import create_demo_store
from store_storage import JsonStoreStorage, StoreCodec


def main() -> None:
    try:
        store = create_demo_store()
        customer_id = 1
        cart = store.get_cart(customer_id)

        cart.add_book(store.catalog.get_book(1))
        paid_order = store.create_order(customer_id)
        store.pay_order(paid_order.id)

        cart.add_book(store.catalog.get_book(2))
        cancelled_order = store.create_order(customer_id)
        store.pay_order(cancelled_order.id, success=False)
        store.cancel_order(cancelled_order.id)

        cart.add_book(store.catalog.get_book(2))

        store.catalog.update_book(
            1,
            "Капитанская дочка — новая редакция",
            Decimal("50.00"),
        )

        file_path = (
            Path(__file__).resolve().parent
            / "data"
            / "store.json"
        )
        storage = JsonStoreStorage(file_path)
        storage.save(store)
        print("Магазин сохранён в data/store.json.")

        restored = storage.load()

        assert StoreCodec.to_dict(restored) == StoreCodec.to_dict(store)
        print("Полное состояние после загрузки совпадает.")

        customer = restored.get_customer(customer_id)
        order = restored.get_order(1)

        print(f"\nПокупатель: {customer.name}")
        print(f"Статус первого заказа: {order.status}")
        print(f"Сумма первого заказа: {order.get_total():.2f} руб.")
        print(
            f"Текущая цена первой книги: "
            f"{restored.catalog.get_book(1).price:.2f} руб."
        )
        print(
            f"Приобретённых книг: "
            f"{len(customer.get_purchased_books())}"
        )
        print(
            f"Прав доступа: "
            f"{len(restored.get_licenses(customer_id))}"
        )
        print(
            f"Статус второго заказа: "
            f"{restored.get_order(2).status}"
        )
        print(
            f"Сумма восстановленной корзины: "
            f"{restored.get_cart(customer_id).get_total():.2f} руб."
        )

        assert order.get_items()[0].book_title == "Капитанская дочка"
        assert order.get_total() == Decimal("199.90")

        new_order = restored.create_order(customer_id)
        print(f"\nНомер следующего заказа: {new_order.id}")
        assert new_order.id == 3

        restored.pay_order(new_order.id)

        print(
            f"Книг после новой покупки: "
            f"{len(customer.get_purchased_books())}"
        )
        print(
            f"Прав доступа после новой покупки: "
            f"{len(restored.get_licenses(customer_id))}"
        )

        assert len(customer.get_purchased_books()) == 2
        assert len(restored.get_licenses(customer_id)) == 2

        print("Проверки восстановления магазина пройдены.")

    except BookStoreError as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
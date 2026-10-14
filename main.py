from catalog import Author, Category, Publisher


def main() -> None:
    author = Author(1, "Александр Пушкин")
    print(f"Создан автор: {author.name}")

    publisher = Publisher(1, "Учебное издательство")
    category = Category(1, "Художественная литература")

    print(f"Издательство: {publisher.name}")
    print(f"Категория: {category.name}")

    publisher.update("Электронная библиотека")
    category.update("Классика")

    print(f"Новое издательство: {publisher.name}")
    print(f"Новая категория: {category.name}")

    try:
        category.update("   ")
    except ValueError as error:
        print(f"Ошибка обработана: {error}")

    print(f"После ошибки категория сохранена: {category.name}")

    author.update(
        "Александр Сергеевич Пушкин",
        "Русский поэт и писатель.",
    )
    print(f"После изменения: {author.name}")

    try:
        author.update("   ", "")
    except ValueError as error:
        print(f"Ошибка обработана: {error}")

    print(f"После ошибки имя сохранено: {author.name}")


if __name__ == "__main__":
    main()
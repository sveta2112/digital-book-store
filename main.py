from catalog import Author


def main() -> None:
    author = Author(1, "Александр Пушкин")
    print(f"Создан автор: {author.name}")

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
import pytest
from library import Library


@pytest.fixture
def library():
    lib = Library(":memory:")
    return lib


def test_add_author(library):
    """
    Тест на добавление автора
    """
    author_id = library.add_author("J.K. Rowling")
    assert author_id is not None, "Автор не был добавлен."


def test_add_genre(library):
    """
    Тест на добавление жанра
    """
    genre_id = library.add_genre("Fantasy")
    assert genre_id is not None, "Жанр не был добавлен."


def test_add_book(library):
    """
    Тест на добавление книги
    """
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    book_id = library.add_book("Harry Potter and the Philosopher's Stone", author_id, 1997, genre_id)
    assert book_id is not None, "Книга не была добавлена."


def test_add_member(library):
    member_id = library.add_member("John Doe")
    assert member_id is not None, "Член библиотеки не был добавлен."


def test_get_books_by_author(library):
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    library.add_book("Harry Potter and the Chamber of Secrets", author_id, 1998, genre_id)
    books = library.get_books_by_author("J.K. Rowling")

    assert len(books) == 1, "Количество книг по автору неверное."
    assert books[0][1] == "Harry Potter and the Chamber of Secrets", "Название книги неверное."


def test_get_available_books(library):
    """
    Проверяем запрос на количество доступных книг
    """
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    library.add_book("Harry Potter and the Goblet of Fire", author_id, 2000, genre_id)
    available_books = library.get_available_books()

    assert len(available_books) == 1, "Количество доступных книг неверное."
    assert available_books[0][1] == "Harry Potter and the Goblet of Fire", "Название книги неверное."


def test_borrow_book(library):
    """
    Проверяем запрос на выдачу книг
    """
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    book_id = library.add_book("Harry Potter and the Order of the Phoenix", author_id, 2003, genre_id)
    member_id = library.add_member("John Doe")
    success = library.borrow_book(book_id, member_id)

    assert success, "Не удалось выдать книгу."
    available_books = library.get_available_books()
    assert len(available_books) == 0, "Книга не была отмечена как недоступная."


def test_search_book(library):
    """
    Проверяем запрос на селект книг
    """
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    library.add_book("Harry Potter and the Half-Blood Prince", author_id, 2005, genre_id)
    books = library.search_book("Harry Potter and the Half-Blood Prince")
    assert len(books) > 0, "Книга не найдена."
    assert books[0][1] == "Harry Potter and the Half-Blood Prince", "Название найденной книги неверное."


def test_sql_injection_in_author_name(library):
    """
    Проверяем sql-инъекции при добавлении автора
    """
    malicious_input = "J.K. Rowling'; DROP TABLE t_author; --"
    library.add_author(malicious_input)
    authors = library.get_books_by_author(malicious_input)
    assert len(authors) == 0, "SQL-инъекция сработала, что недопустимо."


def test_sql_injection_in_search_book(library):
    """
    Проверяем sql-инъекции при поиске книги
    """
    author_id = library.add_author("J.K. Rowling")
    genre_id = library.add_genre("Fantasy")
    library.add_book("Harry Potter and the Deathly Hallows", author_id, 2007, genre_id)

    malicious_input = "Harry Potter'; DROP TABLE t_book; --"
    result = library.search_book(malicious_input)
    assert result == [], "SQL-инъекция сработала, что недопустимо. Или выпала системная ошибка"

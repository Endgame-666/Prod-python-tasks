import sqlite3

from datetime import date

import typing as tp
from typing import List, Any


class Library:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        """
        Таблица t_author
        id - id автора
        text - инициалы автора
        """

        cursor.execute('''
               CREATE TABLE IF NOT EXISTS t_author (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL
               )
           ''')

        """
        Таблица t_genre
        id - id жанра
        text - жанр
        """

        cursor.execute('''
               CREATE TABLE IF NOT EXISTS t_genre (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE NOT NULL
               )
           ''')

        """
        Таблица t_book
        id - id жанра
        title - название книги
        author_id - автор книги
        publication_year - год публикации
        genre_id - индификатор жанра (из таблицы t_genre)
        available - флаг означающий можем ли мы ее взять (по умолчанию можем если она есть)
        """

        cursor.execute('''
               CREATE TABLE IF NOT EXISTS t_book (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   author_id INTEGER,
                   publication_year INTEGER,
                   genre_id INTEGER,
                   available BOOLEAN DEFAULT 1,
                   FOREIGN KEY (author_id) REFERENCES t_author(id),
                   FOREIGN KEY (genre_id) REFERENCES t_genre(id)
               )
           ''')

        """
        Таблица t_member:
        id - ID члена библиотеки
        name - имя читателя
        membership_date - дата записи
        """

        cursor.execute('''
               CREATE TABLE IF NOT EXISTS t_member (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   membership_date DATE NOT NULL
               )
           ''')

        """
        Таблица t_borrowed_book:
        id - ID выданной книги
        book_id - ID книги, которая была выдана
        member_id - ID читателя, которому выдана книга
        borrow_date - дата выдачи книги
        return_date - дата возврата книги
        """
        cursor.execute('''
               CREATE TABLE IF NOT EXISTS t_borrowed_book (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   book_id INTEGER,
                   member_id INTEGER,
                   borrow_date DATE NOT NULL,
                   return_date DATE,
                   FOREIGN KEY (book_id) REFERENCES t_book(id),
                   FOREIGN KEY (member_id) REFERENCES t_member(id)
               )
           ''')

        self.conn.commit()

    def add_author(self, name: str) -> int:
        """
        Добавляет автора в таблицу t_author.
        Возвращаем ID добавленного автора.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO t_author (name) VALUES (?)
        ''', (name,))
        self.conn.commit()
        return cursor.lastrowid

    def add_genre(self, name: str) -> int:
        """
        Добавляет жанр в таблицу t_genre.
        Возвращаем ID добавленного жанра.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO t_genre (name) VALUES (?)
        ''', (name,))
        self.conn.commit()
        return cursor.lastrowid

    def add_book(self, title: str, author_id: int, publication_year=None, genre_id=None) -> int:
        """
        Добавляет книгу в таблицу t_book.
        Возвращаем ID добавленной книги.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO t_book (title, author_id, publication_year, genre_id) VALUES (?, ?, ? ,?)
        ''', (title, author_id, publication_year, genre_id,))
        self.conn.commit()
        return cursor.lastrowid

    def add_member(self, name: str, membership_date="now") -> int:
        """
        Добавляет нового члена библиотеки в таблицу t_member.
        Возвращаем ID добавленного члена.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO t_member (name, membership_date) VALUES (?, ?)
        ''', (name, membership_date,))
        self.conn.commit()
        return cursor.lastrowid

    def get_books_by_author(self, author_name: str) -> tp.List[tp.Any]:
        """
        Достать список книг по имени автора.
        Метод должен возвращать список кортежей всех доступных книг по автору.
        """
        cursor = self.conn.cursor()

        # Получаем ID автора по имени
        cursor.execute('''
            SELECT id FROM t_author WHERE name = ?
        ''', (author_name,))
        author = cursor.fetchone()

        if not author:
            return []

        author_id = author[0]

        cursor.execute('''
            SELECT id, title, author_id
            FROM t_book
            WHERE author_id = ?
        ''', (author_id,))
        books = [
            (
                row[0],
                row[1],
                row[2]
            )
            for row in cursor.fetchall()
        ]
        return books

    def get_available_books(self) -> tp.List[tp.Tuple[tp.Any, tp.Any]]:
        """
        Возвращает список всех доступных книг.
        Метод должен возвращать список кортежей всех доступных книг
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id FROM t_book WHERE available = 1
        ''')
        id_list = [row[0] for row in cursor.fetchall()]
        available_books = []
        for id_ in id_list:
            cursor.execute('''
                SELECT title FROM t_book where id = ?
            ''', (id_,))
            book = cursor.fetchone()
            available_books.append((id_, book[0]))
        return available_books


    def borrow_book(self, book_id: int, member_id: int) -> bool:
        """
        Записывать выдачу книги члену библиотеки.
        Метод должен True если успех иначе False.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT available FROM t_book WHERE id = ?  
        ''', (book_id,))
        avail = cursor.fetchone()
        if avail[0]:
            cursor.execute('''
                INSERT INTO t_borrowed_book (book_id, member_id, borrow_date) VALUES (?, ?, ?) 
            ''', (book_id, member_id, "now",))
            cursor.execute('''
                UPDATE t_book SET available = 0 WHERE id = ?
            ''', (book_id,))
            self.conn.commit()
            return True
        return False

        
    def search_book(self, title: str) -> tp.List[tp.Any]:
        """
        Ищем книгу (по названию) из таблицы книг
        Метод должен возвращать лист кортежей всех по названию!
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title FROM t_book WHERE title = ?
        ''', (title,))
        book = cursor.fetchone()
        if book == None:
            return []
        else:
            return [book]


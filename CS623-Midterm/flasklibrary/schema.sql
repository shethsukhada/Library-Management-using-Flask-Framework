DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS Book_Genre;
DROP TABLE IF EXISTS Book_Publisher;
DROP TABLE IF EXISTS Book;
DROP TABLE IF EXISTS Book_Author;
DROP TABLE IF EXISTS Author;
DROP TABLE IF EXISTS Book_Type;
DROP TABLE IF EXISTS Type;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

--BOOK TABLES

CREATE TABLE Book_Genre(
	book_genre_id int not null primary key,
    genre_name varchar(255)
);

CREATE TABLE Book_Publisher(
	book_publisher_id int not null primary key,
    publisher_name varchar(255)
);

CREATE TABLE Book(
	book_id int not null primary key,
    book_name varchar(255),
    isbn_10 varchar(255),
    isbn_13 varchar(255),
    book_genre_id int,
    book_publisher_id int
);

CREATE TABLE Book_Author(
	book_id int not null,
    author_id int not null,
    author_no int
);

CREATE TABLE Author(
	author_id int not null primary key,
    author_firstname varchar(255),
    author_middlename VARCHAR(255),
    author_lastname varchar(255)
);

CREATE TABLE Book_Type(
	book_id int not null,
    book_type_id int not null,
    unit_price varchar(255)
);

CREATE TABLE Type(
	type_id int not null primary key,
    type_name varchar(255)
);
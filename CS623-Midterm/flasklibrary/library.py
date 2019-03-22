from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('library', __name__)

@bp.route('/',methods=('GET', 'POST'))
def index():
    posts = None
    if g.user is not None:
        print(g.user[3])
        user_role = g.user[3]
        db = get_db()
        if user_role == 'user':
            posts = db.execute(
                'SELECT id, username'
                ' FROM user WHERE id = ?', (g.user[0],)            
            ).fetchall()
            library = db.execute(
                'SELECT user_id, book_id FROM library WHERE user_id = ?', (g.user[0],)
            ).fetchall()
            books = db.execute(
                'SELECT Book.book_id, book_name, genre_name '
                'FROM Book '
                'JOIN Book_Genre on Book.book_genre_id = Book_Genre.book_genre_id '
                'JOIN library on Book.book_id = library.book_id '
                'WHERE library.user_id = ?',(g.user[0],)
            ).fetchall()
            return render_template('library/index.html', posts=posts, books=books)
        elif user_role == 'librarian':
            print(user_role)
            books = db.execute(
                'SELECT book_id, book_name, qty '
                'FROM Book'
            ).fetchall()
            author = db.execute(
                'SELECT author_id, author_firstname, author_middlename, author_lastname '
                'FROM Author'
            ).fetchall()[1:]
            genres = db.execute(
                'SELECT book_genre_id, genre_name FROM book_genre'
            ).fetchall()[1:]
            publishers = db.execute(
                'SELECT book_publisher_id, publisher_name FROM book_publisher'
            ).fetchall()[1:]
            #######################################################################
            # I think is correct, it might need some tweaking, im not sure though #
            #######################################################################
            bookList = db.execute(
                'SELECT b.book_id, b.book_name, a.author_firstname, a.author_middlename, a.author_lastname, b.qty '
                'FROM book as b '
                'JOIN book_author as ba on ba.book_id = b.book_id '
                'JOIN author as a on a.author_id = ba.author_id '
            ).fetchall()
            # auhtor(id, names), genre(id, name) and publisher(id, name) and bookslist(book_title, author_fistlast and middle qty)
            return render_template('library/librarianPortal.html', books=books, authors=author,genres=genres,publishers=publishers,bookList=bookList)
    return render_template('library/index.html')

@bp.route('/books',methods=('GET', 'POST'))
def listBooks():
    if request.method == 'POST':
        print(request.form['books'])
        book = request.form['books']
        print('WHERE book_name = ' + "'" + book + "'")
        if book:
            db = get_db()
            book_id = db.execute(
                'SELECT book_id FROM Book WHERE book_name = ?', (book,)
            ).fetchone()
            print(book_id[0])
            print(g.user[0])
            # insert into library table
            db.execute(
                'INSERT INTO library VALUES(?,?)',(g.user[0],book_id[0])
            )
            db.commit()
            # Decriment the qty by one for the chosen book
            db.execute(
                'UPDATE Book '
                'SET qty = (SELECT qty - 1 FROM Book WHERE book_id = ?) '
                'WHERE book_id = ?', (book_id[0],book_id[0],)
            )
            db.commit()
            return redirect(url_for('index'))

    db = get_db()
    books = db.execute(
        'SELECT book_id, book_name, genre_name '
        'FROM Book '
        'JOIN Book_Genre on Book.book_genre_id = Book_Genre.book_genre_id '
        'WHERE qty > 0 '
        'AND book_id NOT IN (SELECT book_id from library WHERE user_id = ?)', (g.user[0],)
    ).fetchall()
    return render_template('library/listBooks.html', books=books)


    
@bp.route('/aboutbook/<int:book_id>',methods=('GET', 'POST'))
def aboutbook(book_id):
     if book_id:
         db = get_db()
         book_details = db.execute(
                        'SELECT    book.book_id, book_name, genre_name, author_firstname , '
                        'author_middlename , author_lastname , unit_price , type_name '
                        'FROM Book '
                        ' LEFT JOIN Book_Genre on Book.book_genre_id = Book_Genre.book_genre_id '
                        ' LEFT JOIN book_author on book.book_id = book_author.book_id '
                        ' LEFT JOIN author on book_author.author_id = author.author_id '
                        ' LEFT JOIN book_type on book_type.book_id = book.book_id '
                        ' LEFT JOIN type on book_type.book_type_id = type.type_id '
                        ' where book.book_id = ? ',(book_id,)
          ).fetchone()

     return render_template('library/aboutbook.html' , book_details=book_details)

@bp.route('/returnbook/<int:book_id>/<int:user_id>/<string:book_name>',methods=('GET', 'POST'))
def returnbook(book_id,user_id,book_name):
    if book_id and user_id:   
        db = get_db()
        db.execute('DELETE FROM library where user_id = ?  and book_id = ? ', ( user_id , book_id,))
        db.commit()
        # Decriment the qty by one for the chosen book
        db.execute(
                'UPDATE Book '
                'SET qty = (SELECT qty + 1 FROM Book WHERE book_id = ?) '
                'WHERE book_id = ?', (book_id, book_id,)
            )
        db.commit()
    return render_template('library/returnbook.html', book_id = book_id, user_id=user_id , book_name=book_name  )


@bp.route('/trackthebooks/',methods=('GET', 'POST'))
def trackthebooks():    
        db = get_db()
        book_tracker = db.execute(
                        'select user.id, username,  library.book_id , book.book_name , qty '
                        'from library '
                        'inner join user on library.user_id = user.id '
                        'inner join Book on library.book_id = book.book_id;'
                        )
        
        return render_template('library/trackthebooks.html', book_tracker=book_tracker  )

@bp.route('/addbook', methods=['POST'])
def addBook():

    if g.user is not None and g.user[3] == 'librarian':

        db = get_db()
        book_id = request.form['book_id']
        book_title = request.form['book_title']
        book_author_id = request.form['author']
        book_genre_id = request.form['genre']
        book_publisher_id = request.form['publisher']

        # Add the new book to the databases
        db.execute('INSERT INTO Book VALUES(?,?,?,?,?,?,?)', (book_id, book_title, "", "", book_genre_id, book_publisher_id, 10))
        db.execute('INSERT INTO book_author VALUES(?,?,?)', (book_id, book_author_id, 1))
        db.commit()

    return redirect(url_for('index'))
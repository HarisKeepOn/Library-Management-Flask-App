from flask import Flask, render_template, request , redirect, url_for, flash
import sqlite3
import isbnlib
import hashlib
import json
import re

from flask import jsonify
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# from isbnlib import meta

app = Flask(__name__)
app.secret_key = "abc"  

#login route
@app.route('/', methods=['GET', 'POST'])
def login():
    create_user_table()
    
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        # Hash the provided password to compare with the stored hash
        hashed_password = hash_password(password)
        # Check if the user exists and the password is correct
        conn = sqlite3.connect('lms_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE Email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            if hashed_password == user[3]:
                return jsonify({'message': 'Login successful.', 'status': 'success', 'user_id': user[0]}), 200
            else:
                return jsonify({'message': 'Invalid password.', 'status': 'error'}), 400
        else:
            return jsonify({'message': 'User does not exist.', 'status': 'error'}), 400    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    create_user_table()

    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        retypepassword = request.form['retypepassword']

        # Perform basic validation
        if not fullname or not email or not password or not retypepassword:
            return jsonify({"message": "Please fill in all fields.", "status": "error"})

        # Perform email validation
        email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(email_regex, email):
            return jsonify({"message": "Please enter a valid email address.", "status": "error"})

        # Check if the passwords match
        if password != retypepassword:
            return jsonify({"message": "Passwords do not match.", "status": "error"})

        # Hash the password using SHA-256 (Assuming you have the hash_password function defined)
        hashed_password = hash_password(password)

        # Check if the user with the given email already exists
        conn = sqlite3.connect('lms_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE Email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "User with this email already exists.", "status": "error"})

        # Insert the new user into the 'users' table
        cursor.execute("INSERT INTO users (FullName, Email, Password) VALUES (?, ?, ?)", (fullname, email, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({"message": "Registration successful.", "status": "success"})

    return render_template('register.html')

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_user_table():
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "FullName TEXT NOT NULL,"
        "Email TEXT NOT NULL UNIQUE,"
        "Password TEXT NOT NULL"
        ")"
    )
    conn.close()



@app.route('/home', methods=['GET', 'POST'])
def home():
    conn = sqlite3.connect('lms_db.db')
    message = "Connected to the database"
 
    # Handle search functionality
    search_query = request.args.get('search')
    
    if search_query:
       search_results = search_book(search_query)
       print(search_results)
       return jsonify({'books': search_results})

    return render_template('index.html', books=get_saved_books() , message=message)

def search_book(query):
    books_by_isbn = isbnlib.goom(query)

    if books_by_isbn:
        return books_by_isbn
    else:
        return "No books found matching the search query."

def search_books_by_title(title):
    lowercase_title = title.lower()
    isbn = isbnlib.canonical(lowercase_title)
    if isbn:
        book_info = isbnlib.meta(isbn)
        return [book_info]
    else:
        return []

def search_books(query):
    books_by_isbn = search_book(query)
    if books_by_isbn != "No books found matching the search query.":
        return books_by_isbn
    else:
        books_by_title = search_books_by_title(query)
        return books_by_title

def get_saved_books():
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    is_table_exist_and_if_not_then_create()

    # Fetch all the saved books from the 'saved_books' table
    cursor.execute("SELECT * FROM saved_books")
    saved_books = cursor.fetchall()
    
    books = []
    for book in saved_books:
        book_id = book[0]
        title = book[1]
        year = book[2]
        publisher = book[3]
        language = book[4]
        isbn = book[5]
        rating = book[6]
        book_type = book[7]
        current_lend_status = book[8]
        recent_borrower_name = book[9]
        starting_date = book[10]
        end_date = book[11]

        # Retrieve authors for the book
        cursor.execute("SELECT AuthorName FROM authors WHERE BookID = ?", (book_id,))
        authors = [author[0] for author in cursor.fetchall()]


        book_data = {
            'Title': title,
            'Authors': authors,
            'Year': year,
            'Publisher': publisher,
            'Language': language,
            'ISBN-13': isbn,
            'BookType': book_type,
            'CurrentLendStatus': current_lend_status,
            'RecentBorrowerName': recent_borrower_name,
            'StartingDate': starting_date,
            'EndDate': end_date ,
            'Rating': rating
            

        }
        books.append(book_data)

    conn.close()
    return books

def is_table_exist_and_if_not_then_create():
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    # Create the 'saved_books' table if it doesn't exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS saved_books ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "Title TEXT NOT NULL,"
        "Year TEXT,"
        "Publisher TEXT,"
        "Language TEXT,"
        "ISBN TEXT,"
        "Rating INTEGER DEFAULT 1,"
        "BookType TEXT DEFAULT 'N/A',"
        "CurrentLendStatus INTEGER DEFAULT 0,"
        "RecentBorrowerName TEXT,"
        "StartingDate TEXT,"
        "EndDate TEXT,"        
        "UNIQUE (ISBN)"
        ")"
    )
    
    # Create the 'authors' table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS authors ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "AuthorName TEXT NOT NULL,"
        "BookID INTEGER NOT NULL,"
        "FOREIGN KEY (BookID) REFERENCES saved_books (ID)"
        ")"
    )
        
    conn.close()
    

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    message = "Added to Database"
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    # Create the 'saved_books' table if it doesn't exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS saved_books ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "Title TEXT NOT NULL,"
        "Year TEXT,"
        "Publisher TEXT,"
        "Language TEXT,"
        "ISBN TEXT,"
        "Rating INTEGER DEFAULT 1,"
        "BookType TEXT DEFAULT 'N/A',"
        "CurrentLendStatus INTEGER DEFAULT 0,"
        "RecentBorrowerName TEXT,"
        "StartingDate TEXT,"
        "EndDate TEXT,"        
        "UNIQUE (ISBN)"
        ")"
    )
    
    # Create the 'authors' table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS authors ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "AuthorName TEXT NOT NULL,"
        "BookID INTEGER NOT NULL,"
        "FOREIGN KEY (BookID) REFERENCES saved_books (ID)"
        ")"
    )
    

    isbn = request.args.get('isbn')
    rating = request.args.get('rating')
    
    if isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn):
        # Check if the book with the given ISBN already exists in the 'saved_books' table
        cursor.execute("SELECT ID FROM saved_books WHERE ISBN = ?", (isbn,))
        existing_book = cursor.fetchone()
    
        if existing_book:
            # Book with the given ISBN already exists, handle accordingly
            message = "Book with ISBN {} already exists in the database.".format(isbn)
            return jsonify({'message': message , 
                            'status': 409
                            }), 409  # Conflict status code
        else:
            book_info = isbnlib.meta(isbn)
            title = book_info.get('Title')
            year = book_info.get('Year')
            publisher = book_info.get('Publisher')
            language = book_info.get('Language')
            # string to int
            Rating = int(rating) or 1
            
            
           
           # Insert the book into the 'saved_books' table
            cursor.execute(
                "INSERT INTO saved_books (Title, Year, Publisher, Language, ISBN ,Rating) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (title, year, publisher, language, isbn, Rating)
            )
            book_id = cursor.lastrowid
    
            # Insert the authors into the 'authors' table
            authors = book_info.get('Authors', [])
            for author in authors:
                cursor.execute(
                    "INSERT INTO authors (AuthorName, BookID) VALUES (?, ?)",
                    (author, book_id)
                )
    
            conn.commit()
            message = "Book with ISBN {} has been added to the database.".format(isbn)
    else:
        message = "Invalid ISBN: {}".format(isbn)
        return jsonify({'message': message
                        , 'status': 400
                        }), 400  # Bad request status code
    
    conn.close()
    return jsonify({'message': message , 
                    'status': 200,
                    'books': get_saved_books()
                    }), 200  # Success status code


@app.route('/edit-book', methods=['GET', 'POST'])
def edit_book():
    message = "Added to Database"
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    # Create the 'saved_books' table if it doesn't exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS saved_books ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "Title TEXT NOT NULL,"
        "Year TEXT,"
        "Publisher TEXT,"
        "Language TEXT,"
        "ISBN TEXT,"
        "Rating INTEGER DEFAULT 1,"
        "BookType TEXT DEFAULT 'N/A',"
        "CurrentLendStatus INTEGER DEFAULT 0,"
        "RecentBorrowerName TEXT,"
        "StartingDate TEXT,"
        "EndDate TEXT,"        
        "UNIQUE (ISBN)"
        ")"
    )
    
    # Create the 'authors' table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS authors ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "AuthorName TEXT NOT NULL,"
        "BookID INTEGER NOT NULL,"
        "FOREIGN KEY (BookID) REFERENCES saved_books (ID)"
        ")"
    )
    

    isbn = request.args.get('isbn')
    bookType = request.args.get('bookType')
    lended = request.args.get('lended')
    borrowerName = request.args.get('borrowerName')
    borrowInitialDate = request.args.get('borrowInitialDate')
    borrowFinalDate = request.args.get('borrowFinalDate')
    rating = request.args.get('rating')
    
    if isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn):
        cursor.execute("UPDATE saved_books SET BookType = ?, CurrentLendStatus = ?, RecentBorrowerName = ?, StartingDate = ?, EndDate = ?, Rating = ? WHERE ISBN = ?", (bookType, lended, borrowerName, borrowInitialDate, borrowFinalDate, rating, isbn))
        conn.commit()
        
        return jsonify({'message': "Book with ISBN {} has been updated.".format(isbn) , 
                        'status': 200,
                        'books': get_saved_books()
                        }), 200
        
    else:
        return jsonify({'message': "Invalid ISBN: {}".format(isbn)
                        , 'status': 400
                        }), 400
    
    
@app.route('/get-book', methods=['GET', 'POST'])
def get_book():
    message = "Added to Database"
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    # Create the 'saved_books' table if it doesn't exist
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS saved_books ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "Title TEXT NOT NULL,"
        "Year TEXT,"
        "Publisher TEXT,"
        "Language TEXT,"
        "ISBN TEXT,"
        "Rating INTEGER DEFAULT 1,"
        "BookType TEXT DEFAULT 'N/A',"
        "CurrentLendStatus INTEGER DEFAULT 0,"
        "RecentBorrowerName TEXT,"
        "StartingDate TEXT,"
        "EndDate TEXT,"        
        "UNIQUE (ISBN)"
        ")"
    )
    
    # Create the 'authors' table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS authors ("
        "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
        "AuthorName TEXT NOT NULL,"
        "BookID INTEGER NOT NULL,"
        "FOREIGN KEY (BookID) REFERENCES saved_books (ID)"
        ")"
    )
    

    isbn = request.args.get('isbn')
    
    if isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn):
        # Check if the book with the given ISBN already exists in the 'saved_books' table
        cursor.execute("SELECT * FROM saved_books WHERE ISBN = ?", (isbn,))
        existing_book = cursor.fetchone()
    
        if existing_book:
            # Book with the given ISBN already exists, handle accordingly
            return jsonify({'message': "Book with ISBN {} already exists in the database.".format(isbn) , 
                            'status': 200,
                            'book': existing_book
                            }), 200
            
        else:
            return jsonify({'message': "Book with ISBN {} does not exist in the database.".format(isbn) ,
                            'status': 400
                            }), 400



@app.route('/delete-book', methods=['DELETE'])
def delete_book():
    conn = sqlite3.connect('lms_db.db')
    cursor = conn.cursor()
    
    isbn = request.args.get('isbn')
    
    if isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn):
        # Check if the book with the given ISBN already exists in the 'saved_books' table
        cursor.execute("SELECT ID FROM saved_books WHERE ISBN = ?", (isbn,))
        existing_book = cursor.fetchone()
    
        if existing_book:
            # Book with the given ISBN already exists, handle accordingly
            cursor.execute("DELETE FROM saved_books WHERE ISBN = ?", (isbn,))
            conn.commit()
            return jsonify({'message': "Book with ISBN {} has been deleted from the database.".format(isbn) , 
                            'status': 200,
                            'books': get_saved_books()
                            }), 200
            
        else:
            return jsonify({'message': "Book with ISBN {} does not exist in the database.".format(isbn) ,
                            'status': 400
                            }), 400
    




if __name__ == '__main__':
    app.run(debug=True)
    # Run the app using Waitress server instead of the built-in Flask server
    # from waitress import serve
    # serve(app, host='127.0.0.1', port=5000)

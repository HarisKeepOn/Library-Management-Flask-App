# Library Management Flask App

The Library Management Flask App is a web application built with Flask, a lightweight and powerful Python web framework. This app allows users to manage a virtual library, perform book-related operations, and keep track of book details in a database.

## Features

1. **User Registration and Login:**
   - Users can register with their full name, email, and password.
   - Passwords are securely hashed using SHA-256 before storing in the database.

2. **Homepage:**
   - The homepage displays a list of saved books in the library database.
   - Users can search for books by providing either ISBN or book title.
   - The search results are fetched from the `isbnlib` library, which allows searching for books using ISBN numbers.

3. **Add a Book:**
   - Users can add new books to the library by providing the book's ISBN and rating.
   - Book information such as title, year, publisher, language, and authors are automatically fetched using the `isbnlib.meta` function.

4. **Edit Book Details:**
   - Users can edit the details of existing books in the library by providing the book's ISBN.
   - The user can update the book type, lend status, borrower name, lending dates, and rating of the book.

5. **View Book Details:**
   - Users can view detailed information about a book by providing its ISBN.

6. **Delete a Book:**
   - Users can remove a book from the library by providing its ISBN.

## Setup

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Run the application using `python app.py`.
4. The app will be accessible at `http://127.0.0.1:5000/` in your web browser.

## Dependencies

The Library Management Flask App relies on the following Python libraries:

- Flask: A web framework used for creating the application and handling routes.
- sqlite3: A library used to manage the SQLite database.
- isbnlib: A library used to fetch book information based on ISBN numbers.

## Database

The application uses an SQLite database named `lms_db.db` to store user information, saved books, and authors. The required tables (users, saved_books, and authors) are automatically created upon first run.

## Usage

1. Register or log in to the app using your credentials.
2. Use the homepage to view the list of saved books and search for new books.
3. Add new books to the library by providing the book's ISBN and rating.
4. Edit the details of existing books using their ISBN.
5. View detailed information about a book by providing its ISBN.
6. Delete books from the library using their ISBN.

## Screenshots

(TODO: Add screenshots of the app in action)

## Contributing

Contributions to the Library Management Flask App are welcome! If you find any bugs, want to add new features, or improve existing functionality, please feel free to submit a pull request.

## License

The Library Management Flask App is open-source software licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the application for both commercial and non-commercial purposes.

## Acknowledgments

This application was created by Haris Khan.

---

This README provides an overview of the Library Management Flask App, its features, setup instructions, usage guidelines, and licensing information. Feel free to customize the README with more details, such as deployment instructions, additional screenshots, or a more comprehensive guide to using the app.
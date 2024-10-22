from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB Connection
client = MongoClient('your-mongo-connection-string')
db = client['library_db']
books_collection = db['books']
issues_collection = db['issues']


@app.route('/')
def home():
    return render_template('home.html')


# Add a new book
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year = request.form['year']
        books_collection.insert_one({
            'title': title,
            'author': author,
            'genre': genre,
            'year': year,
            'availability': True
        })
        flash('Book added successfully!', 'success')
        return redirect(url_for('list_books'))
    return render_template('add_book.html')


# List all books with search and filter
@app.route('/books', methods=['GET', 'POST'])
def list_books():
    search = request.form.get('search')
    genre = request.form.get('genre')

    query = {}
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}
    if genre:
        query['genre'] = genre

    books = books_collection.find(query)
    return render_template('book_list.html', books=books)


# Issue a book
@app.route('/issue/<book_id>', methods=['GET', 'POST'])
def issue_book(book_id):
    book = books_collection.find_one({'_id': book_id})
    if request.method == 'POST':
        user = request.form['user']
        return_date = request.form['return_date']
        books_collection.update_one({'_id': book_id}, {'$set': {'availability': False}})
        issues_collection.insert_one({
            'book_id': book_id,
            'user': user,
            'issue_date': datetime.now(),
            'return_date': return_date
        })
        flash('Book issued successfully!', 'success')
        return redirect(url_for('list_books'))

    return render_template('issue_book.html', book=book)


# Return a book
@app.route('/return/<book_id>', methods=['POST'])
def return_book(book_id):
    books_collection.update_one({'_id': book_id}, {'$set': {'availability': True}})
    issues_collection.delete_one({'book_id': book_id})
    flash('Book returned successfully!', 'success')
    return redirect(url_for('list_books'))


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb+srv://root:**@cluster1.okylwxq.mongodb.net/library_db?retryWrites=true&w=majority")
db = client['library_db']  # Use your actual database name
books_collection = db['books']

# Home Route - List all books
@app.route('/')
def home():
    books = books_collection.find()
    return render_template('book_list.html', books=books)

# Add Book Route
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        books_collection.insert_one({
            'title': title,
            'author': author,
            'year': year
        })
        return redirect(url_for('home'))
    return render_template('add_book.html')

# Edit Book Route
@app.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        books_collection.update_one(
            {'_id': ObjectId(book_id)},
            {"$set": {'title': title, 'author': author, 'year': year}}
        )
        return redirect(url_for('home'))
    return render_template('edit_book.html', book=book)

# Delete Book Route
@app.route('/delete/<book_id>')
def delete_book(book_id):
    books_collection.delete_one({'_id': ObjectId(book_id)})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

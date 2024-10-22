from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client['library']  # Replace with your database name
books_collection = db['books']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/books')
def book_list():
    books = books_collection.find()
    return render_template('book_list.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        books_collection.insert_one({'title': title, 'author': author, 'year': year})
        return redirect(url_for('home'))
    return render_template('add_book.html')

@app.route('/issue', methods=['GET', 'POST'])
def issue_book():
    books = books_collection.find()
    if request.method == 'POST':
        book_id = request.form['book_id']
        # Logic to issue the book goes here (you can store the issued status)
        return redirect(url_for('home'))
    return render_template('issue_book.html', books=books)

@app.route('/return', methods=['GET', 'POST'])
def return_book():
    books = books_collection.find()
    if request.method == 'POST':
        book_id = request.form['book_id']
        # Logic to return the book goes here (you can store the returned status)
        return redirect(url_for('home'))
    return render_template('return_book.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)

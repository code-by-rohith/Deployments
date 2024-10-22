from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a random secret key for sessions

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client['library_db']  # Use your actual database name
books_collection = db['books']
users_collection = db['users']  # Collection to store user data

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Home Route - Show login and signup
@app.route('/')
def home():
    return render_template('home.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = "user"  # Default role for new users

        if users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different username.', 'danger')
        else:
            users_collection.insert_one({
                'username': username,
                'password': password,
                'role': role
            })
            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user is admin
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            session['role'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('home_admin'))

        # Check for regular users in the database
        user = users_collection.find_one({'username': username, 'password': password})

        if user:
            session['username'] = username
            session['role'] = user['role']  # Store user role (user)
            flash('Login successful!', 'success')
            return redirect(url_for('home_user'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# User Home Route - List all books
@app.route('/home_user')
def home_user():
    books = books_collection.find()
    return render_template('book_list.html', books=books)

# Admin Home Route - List all books with admin options
@app.route('/home_admin')
def home_admin():
    books = books_collection.find()
    return render_template('book_list_admin.html', books=books)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Add Book Route
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['role'] != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        books_collection.insert_one({
            'title': title,
            'author': author,
            'year': year
        })
        flash('Book added successfully!', 'success')
        return redirect(url_for('home_admin'))
    return render_template('add_book.html')

# Edit Book Route
@app.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'username' not in session or session['role'] != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        books_collection.update_one(
            {'_id': ObjectId(book_id)},
            {"$set": {'title': title, 'author': author, 'year': year}}
        )
        flash('Book updated successfully!', 'success')
        return redirect(url_for('home_admin'))
    return render_template('edit_book.html', book=book)

# Delete Book Route
@app.route('/delete/<book_id>')
def delete_book(book_id):
    if 'username' not in session or session['role'] != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    books_collection.delete_one({'_id': ObjectId(book_id)})
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('home_admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

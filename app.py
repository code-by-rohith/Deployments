from flask import Flask, render_template, redirect, request, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'wkjndwjkdnwkjn55'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return f'<User {self.name}>'

@app.route('/')
def main():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', message='Email already exists!'), 400
        
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        session['logged'] = name
        return redirect(url_for('main'))

    return render_template('register.html')

@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('main'))    
    return render_template('edit.html', user=user)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('main'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)


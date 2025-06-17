from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
USER_DB = 'users.txt'
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def user_exists(username):
    if not os.path.exists(USER_DB):
        return False
    with open(USER_DB, 'r') as f:
        for line in f:
            stored_username, _ = line.strip().split(':')
            if username == stored_username:
                return True
    return False
def register_user(username, password):
    hashed_password = hash_password(password)
    with open(USER_DB, 'a') as f:
        f.write(f"{username}:{hashed_password}\n")
def verify_user(username, password):
    hashed_password = hash_password(password)
    with open(USER_DB, 'r') as f:
        for line in f:
            stored_username, stored_password = line.strip().split(':')
            if username == stored_username and hashed_password == stored_password:
                return True
    return False
@app.route('/')
def home():
    if 'username' in session:
        return f"Привет, {session['username']}. <a href='/logout'>Выйти</a>"
    return "<a href='/login'>Войти</a> или <a href='/register'>Зарегистрироваться</a>"
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_user(username, password):
            session['username'] = username
            flash('Вы успешно вошли в систему.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_exists(username):
            flash('Пользователь с таким именем уже существует.', 'danger')
        else:
            register_user(username, password)
            flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)

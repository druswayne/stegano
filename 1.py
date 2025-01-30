from flask import Flask, render_template, request, url_for, redirect, flash, session
from cachelib import FileSystemCache
from flask_session import Session
from datetime import timedelta
import sqlite3

con = sqlite3.connect('data.db', check_same_thread=False)
cursor = con.cursor()
app = Flask(__name__)
app.secret_key = '1234'
app.config['SESSION_TYPE'] = 'cacheLib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='Flask_session', threshold=500)
Session(app)

@app.route("/logout/")
def logout():
    flash(message='Вы вышли из профиля', category='danger')
    return redirect(url_for('login_page'))

@app.route('/login/')
def login_page():
    return render_template('login.html')

@app.route('/')
def main_page():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('login_page'))
    return render_template('main.html')

@app.route('/deshifr/')
def deshifr_page():
    return render_template('deshifr.html')

@app.route('/reg/')
def reg_page():
    return render_template('reg.html')

@app.route('/save_data/', methods=['post'])
def save_data():
    login = request.form['login']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if password != confirm_password:
        flash('Пароли не совпадают!', 'error')
        return redirect(url_for('reg_page'))
    cursor.execute('select * from users where login = (?)', (login,))
    data = cursor.fetchall()
    if data:
        flash('Пользователь с таким именем уже существует', 'error')
        return redirect(url_for('reg_page'))
    cursor.execute('insert into users (login, password) values (?,?)', (login, password))
    con.commit()
    flash('Регистрация успешно завершена!', 'ok')
    return redirect(url_for('login_page'))



@app.route('/auto/', methods=['post'])
def auto_page():
    login = request.form['login']
    password = request.form['password']
    cursor.execute('select * from users where login=(?) and password=(?)',(login, password))
    data = cursor.fetchall()
    if data:
        session['login'] = True
        session['username'] = login
        session.modified = True
        flash('Вы успешно вошли в профиль!', 'ok')
        return redirect(url_for("main_page"))
    flash('неверный логин или пароль', 'error')
    return redirect(url_for('login_page'))



app.run(debug=True, port=1234)
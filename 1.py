from flask import Flask, render_template, request, url_for, redirect, flash, session, send_file
from cachelib import FileSystemCache
from flask_session import Session
from PIL import Image
from steganocryptopy.steganography import Steganography
#from datetime import timedelta
import sqlite3



con = sqlite3.connect('data.db', check_same_thread=False)
cursor = con.cursor()
app = Flask(__name__)
app.secret_key = '1234'
con = sqlite3.connect('data.db', check_same_thread=False)
cursor = con.cursor()

app.config['SESSION_TYPE'] = 'cacheLib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='Flask_session', threshold=500)
Session(app)

@app.route("/logout/")
def logout():
    flash(message='Вы вышли из профиля', category='danger')
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/login/')
def login_page():
    if'login' in session:
        flash('Вы уже вошли в профиль', 'error')
        return redirect(url_for('main_page'))
    return render_template('login.html')

@app.route('/')
def main_page():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'error')
        return redirect(url_for('login_page'))
    return render_template('main.html', login = session['username'])

@app.route('/encrypt/')
def encrypt():
    text_message = request.form['text']
    with open(f'text_message/text_{session["id_user"]}.txt', 'w', encoding='utf-8') as file:
        file.write(text_message)
    image = request.files.get('file')
    image.save(f'input_image/image_{session["id_user"]}.png')
    image_old = Image.open(f'input_image/image_{session["id_user"]}.png')
    rgb_image= image_old.convert('RGB')
    rgb_image.save(f'temp_image/image_{session["id_user"]}.png', format='PNG')
    secret = Steganography.encrypt(f'keys/key_{session["id_user"]}.txt',
                                   f'temp_image/image_{session["id_user"]}.png',
                                   f'text_message/text_{session["id_user"]}.txt')
    secret.save(f'output_image/image_{["id_user"]}.png')
    return send_file(f'output_image/image_{["id_user"]}.png', mimetype='image/*')


@app.route('/decrypt/')
def decrypt():
    image = request.files.get('file')
    image.save(f'shifr_image/image_{session["id_user"]}.png')
    result = Steganography.decrypt(f'keys/key_{session["id_user"]}.txt',
                                   f'shifr_image/image_{session["id_user"]}.png')
    return render_template('deshifr.html', text= result)
@app.route('/deshifr/')
def deshifr_page():
    if 'login' not in session:
        flash('Необходимо авторизоваться', 'danger')
        return redirect(url_for('login_page'))
    return render_template('deshifr.html', login = session['username'])

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
    print(data)
    if data:
        flash('Пользователь с таким именем уже существует', 'error')
        return redirect(url_for('reg_page'))
    cursor.execute('insert into users (login, password) values (?,?)', (login, password))
    con.commit()
    cursor.execute('select id from users where login = (?)', (login,))
    id_user = cursor.fetchone()[0]
    Steganography.generate_key(f'keys/key_{id_user}.txt')
    with open(f'keys/key_{id_user}.txt', 'r', encoding='utf-8') as file:
        key_user = file.read()
    cursor.execute('update users set key = (?) where id = (?)', (key_user, id_user))
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
        session.permanent = False
        session.modified = True
        cursor.execute('select id from users where login = (?)', (login,))
        id_user= cursor.fetchone()[0]
        session['id_user'] = id_user
        flash('Вы успешно вошли в профиль!', 'ok')
        return redirect(url_for("main_page"))
    flash('неверный логин или пароль', 'error')
    return redirect(url_for('login_page'))



app.run(debug=True, port=1234)
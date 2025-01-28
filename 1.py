from flask import Flask, render_template, request, url_for, redirect, flash
import sqlite3
app = Flask(__name__)
app.secret_key = '1234'
con = sqlite3.connect('data.db', check_same_thread=False)
cursor = con.cursor()

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/main/')
def main_page():
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
    cursor.execute('select * from users where login = (?)', (login,))
    data = cursor.fetchall()
    if data:
        return redirect(url_for('reg_page'))
    cursor.execute('insert into users (login, password) values (?,?)', (login, password))
    con.commit()
    return redirect(url_for('login_page'))



@app.route('/auto/', methods=['post'])
def auto_page():
    login = request.form['login']
    password = request.form['password']
    cursor.execute('select * from users where login=(?) and password=(?)',(login, password))
    data = cursor.fetchall()
    if data:
        return redirect(url_for("main_page"))
    flash('неверный логин или пароль', 'error')
    return redirect(url_for('login_page'))



app.run(debug=True, port=1234)
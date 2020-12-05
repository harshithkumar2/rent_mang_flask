from flask import Flask, render_template, request, session, url_for, redirect, flash
import os
from passlib.hash import pbkdf2_sha256
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = os.urandom(16)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'rent_flask'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register')
def reg():
    return render_template('register.html')


@app.route('/regdata', methods=['GET', 'POST'])
def regdata():
    if request.method == 'POST':
        mail = request.form['mail']
        pasw = request.form['pass']
        adr1 = request.form['adr1']
        adr2 = request.form['adr2']
        city = request.form['city']
        state = request.form['state']
        pin = request.form['pin']
        hash_pasw = pbkdf2_sha256.hash(pasw)
        db = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        db.execute('SELECT mail FROM reg WHERE mail=%s', (mail,))
        duplicate = db.fetchone()
        if duplicate is not None:
            if duplicate['mail'] == mail:
                flash('E-mail already exists', 'error')
                db.close()
                return redirect(url_for('register'))
        else:
            db.execute('INSERT INTO reg (mail,password,adress1,adress2,city,state,pin) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                       (mail, hash_pasw, adr1, adr2, city, state, pin))
            mysql.connection.commit()
            db.close()
            flash('Registration Successfull', 'success')
            return redirect(url_for('login'))
    else:
        flash('Please enter correct details', 'error')
        return redirect(url_for('register'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logdata', methods=['POST'])
def logdata():
    if request.method == 'POST':
        mail = request.form['mail']
        pasw = request.form['pass']
        db = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        db.execute("SELECT * FROM reg WHERE mail=%s", (mail,))
        data = db.fetchone()
        if data is None:
            flash('Email not found', 'error')
            db.close()
            return redirect(url_for('login'))
        else:
            if pbkdf2_sha256.verify(pasw, data['password']):
                session['loggedin'] = True
                session['log_mail'] = data['mail']
                db.close()
                return redirect('dashboard')
            else:
                flash('Incorrect Password', 'error')
                db.close()
                return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'loggedin' in session and 'log_mail' in session:
        session.clear()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/dashboard')
def dash():
    if 'loggedin' in session and 'log_mail' in session:
        db = mysql.connection.cursor()
        db.execute('SELECT * FROM client')
        all_data = db.fetchall()
        return render_template('dashboard.html', data=all_data)
    else:
        return redirect(url_for('login'))


@app.route('/add_client')
def add():
    if 'loggedin' in session and 'log_mail' in session:
        return render_template('client.html')
    else:
        return redirect(url_for('login'))


@app.route('/client_data', methods=['GET', 'POST'])
def client():
    if 'loggedin' in session and 'log_mail' in session:
        if request.method == 'POST':
            mail = request.form['mail']
            door_no = request.form['door']
            address = request.form['address']
            phone = request.form['ph']
            city = request.form['city']
            state = request.form['state']
            pin = request.form['pin']
            db = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            db.execute('SELECT mail FROM client WHERE mail=%s', (mail,))
            client = db.fetchone()
            if client is not None:
                flash('client email already registered', 'error')
                db.close()
                return redirect('add_client')
            else:
                db.execute('INSERT INTO client (mail,door_no,address,phone,city,state,pin) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                           (mail, door_no, address, phone, city, state, pin,))
                mysql.connection.commit()
                db.close()
                flash('Client Successfully added', 'success')
                return redirect('dashboard')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/client/<int:id>')
def edit(id):
    if 'loggedin' in session and 'log_mail' in session:
        db = mysql.connection.cursor()
        db.execute('SELECT * FROM client WHERE id=%s', (id,))
        data = db.fetchone()
        db.close()
        return render_template('client_edit.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/client/client_edit/<int:id>', methods=['POST'])
def client_edit(id):
    if 'loggedin' in session and 'log_mail' in session:
        if request.method == 'POST':
            mail = request.form['mail']
            door_no = request.form['door']
            address = request.form['address']
            phone = request.form['ph']
            city = request.form['city']
            state = request.form['state']
            pin = request.form['pin']
            db = mysql.connection.cursor()
            db.execute('UPDATE client SET mail=%s,door_no=%s,address=%s,phone=%s,city=%s,state=%s,pin=%s WHERE id=%s',(mail,door_no,address,phone,city,state,pin,id,))
            mysql.connection.commit()
            db.close()
            flash('Updated Successfully','success')
            return redirect(url_for('dash'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/receipt/<int:id>')
def rec(id):
    if 'loggedin' in session and 'log_mail' in session:
        db = mysql.connection.cursor()
        db.execute('SELECT * FROM client WHERE id=%s', (id,))
        data = db.fetchone()
        db.close()
        return render_template('receipt.html', data=data)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

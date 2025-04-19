from flask import Flask, render_template, request, g, session, url_for, redirect
import sqlite3
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from os import urandom
import base64

app = Flask(__name__)
app.secret_key = '11111111111111'

DB_PATH = './database/donatonDB.db'

# aes key stuff
def make_key(save_path):
    with open(save_path, 'wb') as f:
        f.write(urandom(32))

def get_key(key_path):
    key = ''
    with open(key_path, 'rb') as f:
        key = f.read()
    return key

# only run once to generate 32byte (256bit) aes key and save
#make_key('./key')

iv = b'aaaaaaaaaaaaaaaa'

# database stuff - from docs
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = get_db()

        hashed_pwd = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        cur = connection.cursor()
        cur.execute("SELECT * FROM users where username=? and password=?", (request.form["username"], hashed_pwd))
        row = cur.fetchone()

        if row is None:
            return render_template("login.html", msg='Invalid credentials')

        # login successful
        session['username'] = row[1]
        return redirect(url_for('index'))

    else:
        return render_template("login.html", msg='')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connection = get_db()

        cur = connection.cursor()

        hashed_pwd = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        # AES encryption
        key = get_key('key')
        padder = padding.PKCS7(128).padder()
        x = str.encode(request.form['phone'])
        x_pad = padder.update(x) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        encrypted_phone = enc.update(x_pad) + enc.finalize()

        cur.execute('insert into users(username, name, year, phone, password) values (?, ?, ?, ?,  ?)',
                          (request.form['username'], request.form['name'], request.form['year'], base64.b64encode(encrypted_phone).decode('utf-8'), hashed_pwd))
        connection.commit()

        connection.close()

        return render_template('register.html', msg='Success')
    else:
        return render_template("register.html", msg='')

@app.route("/")
def index():
    if 'username' not in session:
        return render_template('index.html', loggedIn=False)

    connection = get_db()
    cur = connection.cursor()

    namelike_param = ''
    if 'namelike' in request.args:
        namelike_param = request.args['namelike']

    cur.execute('SELECT username, name, phone FROM users where username like ?;',
                ("%"+namelike_param+"%",))
    rows = cur.fetchall()

    # decrypt the phones
    key = get_key('key')
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    decrypted_rows = []
    for r in rows:
        decrypted_rows.append([])
        for i in range(len(r)):
            if i == 2: # phone, need to decrypt here
                decrypt = cipher.decryptor()
                unpadder = padding.PKCS7(128).unpadder()
                x_pad = decrypt.update(base64.b64decode(r[i])) + decrypt.finalize()
                decrypted_rows[-1].append((unpadder.update(x_pad) + unpadder.finalize()).decode('utf-8'))
            else:
                decrypted_rows[-1].append(r[i])

    return render_template("index.html", loggedIn=True, rows=decrypted_rows, username=session['username'])



if __name__ == '__main__':

    app.run(host='localhost', port=5000, debug=True)
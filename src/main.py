from flask import Flask, render_template, request, g, session, url_for, redirect
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '11111111111111'

DB_PATH = './database/database.db'

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
        cur.execute(f'SELECT * FROM users where username="{request.form["username"]}" and'
                    f' password="{hashed_pwd}"')
        row = cur.fetchone()

        if row is None:
            return render_template("login.html", msg='Invalid credentials')

        # login successful
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    else:
        return render_template("login.html", msg='')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connection = get_db()

        cur = connection.cursor()

        hashed_pwd = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        query = (f'insert into users(username, name, password) values '
                 f'("{request.form['username']}", "{request.form['name']}", "{hashed_pwd}")')

        cur.executescript(query)
        connection.commit()

        #
        # print(f'SELECT * FROM users where username="{request.form["username"]}"')
        # cur.execute(f'SELECT * FROM users where username="{request.form["username"]}"')
        # row = cur.fetchall()
        # print(row)

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

    print(f'SELECT username, name FROM users where username like "{namelike_param}";')
    cur.execute(f'SELECT username, name FROM users where username like "%{namelike_param}%";')
    rows = cur.fetchall()
    print(rows)

    return render_template("index.html", loggedIn=True, rows=rows)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
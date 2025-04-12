from flask import Flask, render_template, request, g
import sqlite3
import hashlib

app = Flask(__name__)

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
        cur.executescript(f'SELECT * FROM users where username="{request.form["username"]}" and'
                    f' password="{hashed_pwd}"')
        row = cur.fetchone()

        if row is None:
            return render_template("login.html", msg='Invalid credentials')

        # login successful
        return render_template('index.html', name=row[2], id=row[0])

    else:
        return render_template("login.html", msg='')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connection = get_db()

        hashed_pwd = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        query = (f'insert into users(username, name, password) values '
                 f'("{request.form['username']}", "{request.form['name']}", "{hashed_pwd}")')

        connection.cursor().execute(query)

        connection.commit()
        connection.close()


        return render_template('login.html')
    else:
        return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

DB_PATH = './database/database.db'

# database stuff - from docs
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connection = get_db()

        query = (f'insert into users(username, name, password) values '
                 f'("{request.form['username']}", "{request.form['name']}", "{request.form['password']}")')

        print(query)

        connection.cursor().execute(query)

        connection.commit()
        connection.close()


        return render_template('index.html')
    else:
        return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
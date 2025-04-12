from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pass
    else:
        return render_template("register.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
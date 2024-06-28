from flask import Flask, render_template

app=Flask(__name__)


@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")

@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")

@app.route('/login',methods=["POST"])
def login():
    return render_template("dash.html")

@app.route('/logout')
def logout():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)
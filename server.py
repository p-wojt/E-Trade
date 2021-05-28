from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        pass


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        pass


@app.route('/profile', methods=['POST', 'GET'])
def user_proile():
    if request.method == 'GET':
        return render_template('profile.html') #msg = User


app.run()
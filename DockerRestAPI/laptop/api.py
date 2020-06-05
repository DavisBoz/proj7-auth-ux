# Laptop Service
from flask import Flask, request, session
import flask
from flask import request
from flask_wtf.csrf import CSRFProtect
from flask_restful import Resource, Api
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, 
                            confirm_login, fresh_login_required)
import pymongo
from pymongo import MongoClient
import os
import time
from random import randint
from wtforms import Form, BooleanField, StringField, validators, PasswordField
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

# Instantiate the app
app = Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = ('/api/login')

app.config['SECRET_KEY'] = "this is a secret, huh?"


client = MongoClient("db", 27017)
db = client.tododb
users = db.userdb


class RegisterForm(Form):
    username = StringField('Username', validators=[validators.DataRequired(message=u'Enter username')])
    password = StringField('Password', validators=[validators.DataRequired(message=u'Enter password')])

    
class LoginForm(Form):
    username = StringField('Username', validators=[validators.DataRequired(message=u'Enter username')])
    password = StringField('Password', validators=[validators.DataRequired(message=u'Enter password')])
    remember = BooleanField('Remember Me')


class UserData(UserMixin):
    def __init__(self, user_id):
        self.id = str(user_id)


@app.route("/api/register", methods=["GET", "POST"])
def register():

    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data
    newUser = "" 

    if form.validate():
        item = db.tododb.find_one({"username":username})
        newUser = randint(1,50000)

        if (username == None) or (password == None):
            return 'No username or password given', 400
        if item != None:
            return 'Username taken, try a different username', 400

        pw = pwd_hash(password)
        user = {"_id": newUser, 'username': username, 'password': pw}
        users.insert_one(user)
        result = {'location': newUser, 'username': username, 'password': pw}
        return flask.jsonify(result=result), 201

    return flask.render_template('register.html', form=form)


@login_manager.user_loader
def load_user(user):
    userData = users.find({"_id": int(user)})
    if (userData == None):
        return None
    return UserData(user)


def pwd_hash(password):
    return pwd_context.encrypt(password)


def pwd_verify(password, hashV):
    return pwd_context.verify(password, hashV)


def gen_token(user, expiration=600):
    key = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    token = key.dumps({'id': user})
    return {'token': token, 'duration': expiration}


def verify_token(token):
    key = Serializer(app.config['SECRET_KEY'])
    try:
        data = key.loads(token)
    except SignatureExpired:
        return None    
    except BadSignature:
        return None    
    return "Success"

@app.route("/api/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    
    if (request.method == "POST") and (form.validate()):
        username = form.username.data
        password = form.password.data
        rememberl = form.remember.data
        userData = users.find({"username":username})

        try:
            userData[0]
        except IndexError:
            return redirect(url_for("register"))
        
        entry = userData[0]
        hashValue = entry['password']
        if pwd_verify(password, hashValue) is True:
            currId = entry['_id']
            session['user_id'] = currId
            user = UserData(currId)
            login_user(user, remember = rememberl)
            return redirect(request.args.get("next") or url_for("token"))
        else: return redirect(url_for("register"))         
    return flask.render_template('login.html', form=form)


@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    return "You've been Logged out"


@app.route("/")
def index():
    return flask.render_template("index.html")

              
@app.route("/api/token", methods=['GET'])
@login_required
def token():
    user_id = session.get('user_id')
    tokenData = gen_token(user_id, 600)
    token = tokenData['token']
    token = token.decode('utf-8')
    result = {'token': token, 'duration': 60}
    return flask.jsonify(result=result)


class all_l(Resource):
    def get(self):
        token = request.args.get('token')
        
        if token == None:
            return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None:
            return 'Token could not be verified', 401

        top = request.args.get("top")
        
        if (top == None): top = 20
        _items = db.tododb.find().sort("openTime", pymongo.ASCENDING).limit(int(top))
        items = [item for item in _items]
        return {
            'Open': [item['open_times'] for item in items],
            'Close': [item['close_times'] for item in items]
        }


class all_json(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("openTime", pymongo.ASCENDING).limit(int(top))
        items = [item for item in _items]
   
        return {
            'Open': [item['open_times'] for item in items],
            'Close': [item['close_times'] for item in items]
        }

class all_csv(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Open", pymongo.ASCENDING).limit(int(top))
        items = [item for item in _items]

        csv = ""
        for item in items:
            csv += item['open_times'] + ', ' + item['close_times'] + ', '

        return csv

class open_l(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Open", pymongo.ASCENDING).limit(int(top))

        return {
            'Open': [item['open_times'] for item in _items]
        }

class open_json(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Open", pymongo.ASCENDING).limit(int(top))
        
        return {
            'Open': [item['open_times'] for item in _items]
        }

class open_csv(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Open", pymongo.ASCENDING).limit(int(top))
        items = [item for item in _items]

        csv = ""
        for item in items:
            csv += item['open_times'] + ', '
        return csv

class close_l(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Close", pymongo.ASCENDING).limit(int(top))

        return {
            'Close': [item['close_times'] for item in _items]
        }

class close_json(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Close", pymongo.ASCENDING).limit(int(top))

        return {
            'Close': [item['close_times'] for item in _items]
        }

class close_csv(Resource):
    def get(self):
        token = request.args.get('token')
        if token == None: return 'Please provide a token value in the URL', 401
        verify = verify_token(token)
        if verify == None: return 'Token could not be verified', 401
        
        top = request.args.get("top")
        if (top == None): top = 20

        _items = db.tododb.find().sort("Close", pymongo.ASCENDING).limit(int(top))
        items = [item for item in _items]


        csv = ""
        for item in items:
            csv += item['close_times'] + ', '
        return csv


api.add_resource(all_l, '/listAll')
api.add_resource(all_json, '/listAll/json')
api.add_resource(all_csv, '/listAll/csv')

api.add_resource(open_l, '/listOpenOnly')
api.add_resource(open_json, '/listOpenOnly/json')
api.add_resource(open_csv, '/listOpenOnly/csv')

api.add_resource(close_l, '/listCloseOnly')
api.add_resource(close_json, '/listCloseOnly/json')
api.add_resource(close_csv, '/listCloseOnly/csv')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

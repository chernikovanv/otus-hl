import os
from flask import Flask, jsonify
#from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

DB_HOST = "db"
DB_NAME = os.getenv('MYSQL_DATABASE')
DB_USER = "root"
DB_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')

DROP_TABLE_USERS = '''DROP TABLE IF EXISTS users'''

CREATE_TABLE_USERS = '''
CREATE TABLE IF NOT EXISTS users (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  email varchar(255) DEFAULT NULL,
  password varchar(255) DEFAULT NULL,
  name varchar(255) DEFAULT NULL,
  surname varchar(255) DEFAULT NULL,
  age int(8) unsigned DEFAULT NULL,
  gender enum('male','female') DEFAULT NULL,
  city varchar(50) DEFAULT NULL,
  interests set('travel','sports','dancing') DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (email)
)
'''

DROP_TABLE_FRIENDS = '''DROP TABLE IF EXISTS friends'''

CREATE_TABLE_FRIENDS = '''
CREATE TABLE IF NOT EXISTS friends (
  user_id_1 int(10) unsigned NOT NULL,
  user_id_2 int(10) unsigned NOT NULL
)
'''

class User(UserMixin):
    def __init__(self, id, email, password, name=None, surname=None, age=None, gender=None, city=None, interests=None):
        self.id = id
        self.email = email
        self.password = password 
        self.name = name 
        self.surname = surname 
        self.age = age 
        self.gender = gender 
        self.city = city 
        self.interests = interests 
        
class DBManager:
    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD):
        self.connection = mysql.connector.connect(
            user=user, 
            password=password,
            host=host, # name of the mysql service as set in the docker-compose file
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor()
    
    def init_db(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(DB_NAME))
        self.cursor.execute("USE {}".format(DB_NAME))
        #self.cursor.execute(DROP_TABLE_USERS)
        self.cursor.execute(CREATE_TABLE_USERS)
        #self.cursor.execute(DROP_TABLE_FRIENDS)
        self.cursor.execute(CREATE_TABLE_FRIENDS)
        #self.cursor.executemany('INSERT INTO users (id, email) VALUES (%s, %s);', [(i, 'user_%d@mail.ru'% i) for i in range (1,5)])
        self.connection.commit()
    
    def query_users(self):
        self.cursor.execute('SELECT email FROM users')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec
     
    def query_user_by_email(self, email):
        self.cursor.execute("SELECT id, email, password, name, surname, age, gender, city, interests FROM users where email = '{}'".format(email))
        user = None
        for c in self.cursor:
            user = User(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],list(c[8]))
            break
        return user
    
    def query_user_by_id(self, id):
        self.cursor.execute("SELECT id, email, password, name, surname, age, gender, city, interests FROM users where id = {}".format(id))
        user = None
        for c in self.cursor:
            user = User(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],list(c[8]))
            break
        return user
      
    def add_user(self, email, password, name, surname, age, gender, city, interests):
        SQL = "INSERT INTO users (email, password, name, surname, age, gender, city, interests) VALUES ('{}','{}','{}','{}',{},'{}','{}','{}')"
        self.cursor.execute(SQL.format(email, password, name, surname, age, gender, city, interests))
        self.connection.commit()     

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret-key-goes-here"

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    return db_conn.query_user_by_id(id)
    
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_email(current_user.email)
    
    return render_template('profile.html',
                           name=user.name,
                           surname=user.surname,
                           gender=user.gender,
                           age=user.age,
                           city=user.city,
                           interests=', '.join(user.interests)
                          )
@main.route('/all_profiles')
@login_required
def all_profiles():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_email(current_user.email)
    
    return render_template('all_profiles.html',
                           name=user.name,
                           surname=user.surname
                          )
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')
    age = request.form.get('age')
    gender = request.form.get('gender')
    city = request.form.get('city')
    interests = request.form.getlist('interests')
  
    app.logger.info(interests)
    
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_email(email)
    
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # add the new user to the database
    db_conn.add_user(email=email,
                     password=generate_password_hash(password, method='sha256'),
                     name=name,
                     surname=surname,
                     age=age,
                     gender=gender,
                     city=city,
                     interests=",".join(interests)
                    )

    return redirect(url_for('auth.login'))
 
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_email(email)

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))
  
app.register_blueprint(auth)
app.register_blueprint(main)

db_conn = None
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

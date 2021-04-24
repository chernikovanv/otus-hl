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

GET_FRIENDS = '''
select user_id_2 as id from friends where user_id_1 = {}
union all 
select user_id_1 as id from friends where user_id_2 = {}
'''

class User(UserMixin):
    def __init__(self, id, email=None, password=None, name=None, surname=None, age=None, gender=None, city=None, interests=None):
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
    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME):
        self.host = host
        self.user = user
        self.password = password
        self.database=database
        #self.connection = mysql.connector.connect(
        #    user=self.user, 
        #    password=self.password,
        #    host=self.host,
        #    #database=self.database, 
        #    auth_plugin='mysql_native_password'
        #)
        #self.cursor = self.connection.cursor()
        
    def reconnect(self):
        self.connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            database=self.database,
            auth_plugin='mysql_native_password'
        )
        #self.cursor = self.connection.cursor()
    
    def init_db(self):
        connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            database=self.database, 
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(DB_NAME))
        #cursor.execute("USE {}".format(DB_NAME))
        #self.cursor.execute(DROP_TABLE_USERS)
        cursor.execute(CREATE_TABLE_USERS)
        #self.cursor.execute(DROP_TABLE_FRIENDS)
        cursor.execute(CREATE_TABLE_FRIENDS)
        #self.cursor.executemany('INSERT INTO users (id, email) VALUES (%s, %s);', [(i, 'user_%d@mail.ru'% i) for i in range (1,5)])
        connection.commit()
        cursor.close()
        connection.close()
    
    def query(self, SQL):
      res = []
      try:
        connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            database=self.database, 
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        cursor.execute(SQL)
        res = cursor.fetchall()
        cursor.close()
        connection.close()
      except mysql.connector.errors.DatabaseError as err:
          app.logger.error(err)
          #app.logger.info('db reconnection')
          #self.reconnect()
          #cursor = self.connection.cursor(buffered=True)
          #cursor.execute(SQL)
      return res
    
    def update(self, SQL):
      try:
        connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            database=self.database, 
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        cursor.execute(SQL)
        connection.commit()
        cursor.close()
        connection.close()
      except mysql.connector.errors.DatabaseError as err:
          app.logger.error(err)
          #app.logger.info('db reconnection')
          #self.reconnect()
          #cursor = self.connection.cursor(buffered=True)
          #cursor.execute(SQL)
    
    def query_users(self):
        SQL = 'SELECT id, name, surname FROM users'
        res = self.query(SQL)
        users = []
        for c in res:
            users.append(User(id=c[0], name=c[1], surname=c[2]))
        return users
      
    def query_users_by_pref(self, name_pref, surname_pref):
        SQL = "SELECT id, name, surname FROM users where name like '{}%' and surname like '{}%' order by id asc".format(name_pref, surname_pref)
        res = self.query(SQL)
        users = []
        for c in res:
            users.append(User(id=c[0], name=c[1], surname=c[2]))
        return users
      
    def query_users_by_ids(self, ids):
        if not ids: return []
        SQL = "SELECT id, name, surname FROM users where id in ({})".format(','.join(str(id) for id in ids))
        res = self.query(SQL)
        users = []
        for c in res:
            users.append(User(id=c[0],name=c[1],surname=c[2]))
        return users
     
    def query_user_by_email(self, email):
        SQL = "SELECT id, email, password, name, surname, age, gender, city, interests FROM users where email = '{}'".format(email)
        res = self.query(SQL)
        user = None
        for c in res:
            user = User(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],list(c[8]))
            break
        return user
    
    def query_user_by_id(self, id):
        SQL = "SELECT id, email, password, name, surname, age, gender, city, interests FROM users where id = {}".format(id)
        res = self.query(SQL)
        user = None
        for c in res:
            user = User(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],list(c[8]))
            break
        return user
      
    def add_user(self, email, password, name, surname, age, gender, city, interests):
        SQL = "INSERT INTO users (email, password, name, surname, age, gender, city, interests) VALUES ('{}','{}','{}','{}',{},'{}','{}','{}')"
        SQL = SQL.format(email, password, name, surname, age, gender, city, interests)
        self.update(SQL)
        
    def get_friends(self,id):
        res = self.query(GET_FRIENDS.format(id,id))
        friends = []
        for c in res:
            friends.append(c[0])
        return friends
      
    def become_friends(self,user_id_1,user_id_2):
        SQL = "INSERT INTO friends (user_id_1,user_id_2) VALUES ({},{})".format(user_id_1,user_id_2)
        self.update(SQL)

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
  
@main.route('/profiles_by_pref')
def profiles_by_pref():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
        
    users = db_conn.query_users_by_pref('Br','Al')
    
    return render_template('all_profiles.html',
                           users=users
                          )

@main.route('/profile')
@login_required
def profile():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_email(current_user.email)
    
    friends = db_conn.query_users_by_ids(db_conn.get_friends(user.id))
    
    return render_template('profile.html',
                           name=user.name,
                           surname=user.surname,
                           gender=user.gender,
                           age=user.age,
                           city=user.city,
                           interests=', '.join(user.interests),
                           friends=friends
                          )
  
@main.route('/profile/<id>')
@login_required
def profile_by_id(id):
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    user = db_conn.query_user_by_id(id)
    
    current_user_friends = db_conn.get_friends(current_user.id)
      
    is_friend = user.id in current_user_friends
    is_current_user = current_user.id == user.id
    
    friends = db_conn.query_users_by_ids(db_conn.get_friends(user.id))
    
    return render_template('profile.html',
                           name=user.name,
                           surname=user.surname,
                           gender=user.gender,
                           age=user.age,
                           city=user.city,
                           interests=', '.join(user.interests),
                           id=user.id,
                           is_friend=is_friend,
                           is_current_user=is_current_user,
                           friends=friends
                          )

@main.route('/become_friends', methods=['POST'])
@login_required
def become_friends():
    user_id = request.form.get('user_id')
    
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    friends = db_conn.get_friends(current_user.id)
    
    if user_id not in friends:
      db_conn.become_friends(current_user.id,user_id)
    
    return redirect(request.headers.get("Referer"))
  
@main.route('/all_profiles')
@login_required
def all_profiles():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    users = db_conn.query_users()
    
    return render_template('all_profiles.html',
                           users=users
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
  
    #app.logger.info(interests)
    
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    
    try:
      user = db_conn.query_user_by_email(email)

      if user: # if a user is found, we want to redirect back to signup page so user can try again
          flash('Email address already exists.')
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
    except:
      flash('Some of your data is wrong.') 
      return redirect(url_for('auth.signup'))
 
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

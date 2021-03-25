import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template
import mysql.connector

DB_HOST = "db"
DB_NAME = os.getenv('MYSQL_DATABASE')
DB_USER = "root"
DB_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')

CREATE_TABLE_USERS = '''
CREATE TABLE IF NOT EXISTS users (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  email varchar(255) DEFAULT NULL,
  password varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (email)
)
'''

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
        self.cursor.execute(CREATE_TABLE_USERS)
        #self.cursor.executemany('INSERT INTO users (id, email) VALUES (%s, %s);', [(i, 'user_%d@mail.ru'% i) for i in range (1,5)])
        self.connection.commit()
    
    def query_users(self):
        self.cursor.execute('SELECT email FROM users')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

db_auth = SQLAlchemy()
app = Flask(__name__)

app.config['SECRET_KEY'] = "secret-key-goes-here"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{}:{}@{}/{}".format(DB_USER,DB_PASSWORD,DB_HOST,DB_NAME)

db_auth.init_app(app)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    return 'Logout'
  
app.register_blueprint(auth)
app.register_blueprint(main)

db_conn = None

OLD = '''@app.route('/')
def welcome():
    return jsonify({'status': 'api working'})

@app.route('/users')
def users():
    global db_conn
    if not db_conn: 
      db_conn = DBManager()
      db_conn.init_db()
    rec = db_conn.query_users()

    response = ''
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>'
    return response'''
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

import os
from flask import Flask, jsonify
import mysql.connector

DB_NAME = os.getenv('MYSQL_DATABASE')
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
    def __init__(self, host="db", user="root", password=DB_PASSWORD):
        self.connection = mysql.connector.connect(
            user=user, 
            password=password,
            host=host, # name of the mysql service as set in the docker-compose file
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor()
    
    def init_db():
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(DB_NAME))
        self.cursor.execute(CREATE_TABLE_USERS)
        self.cursor.executemany('INSERT INTO users (id, email) VALUES (%s, %s);', [(i, 'user_%d@mail.ru'% i) for i in range (1,5)])
        self.connection.commit()
    
    def query_users(self):
        self.cursor.execute('SELECT email FROM users')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec
    
app = Flask(__name__)

db_conn = DBManager()
db_conn.init_db()

@app.route('/')
def welcome():
    return jsonify({'status': 'api working'})

@app.route('/users')
def users():
    global db_conn
    if not db_conn: db_conn = DBManager()
    rec = db_conn.query_users()

    response = ''
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>'
    return response
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

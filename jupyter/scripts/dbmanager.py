import os
import mysql.connector

DB_HOST = "db"
DB_NAME = os.getenv('MYSQL_DATABASE')
DB_USER = "root"
DB_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')

DB_NAME = "social_net"
DB_PASSWORD = "root"
                
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

class User():
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
        self.connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            #database=self.database, 
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor()
        
    def reconnect(self):
        self.connection = mysql.connector.connect(
            user=self.user, 
            password=self.password,
            host=self.host,
            database=self.database,
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
    
    def query(self, SQL):
      try:
        self.cursor.execute(SQL)
      except mysql.connector.errors.DatabaseError as err:
          print(err)
          print('db reconnection')
          self.reconnect()
          self.cursor.execute(SQL)
      res = self.cursor.fetchall()
      return res
    
    def update(self, SQL):
      try:
        self.cursor.execute(SQL)
      except mysql.connector.errors.DatabaseError as err:
          print(err)
          print('db reconnection')
          self.reconnect()
          self.cursor.execute(SQL)
      self.connection.commit()
    
    def query_users(self):
        SQL = 'SELECT id, name, surname FROM users'
        res = self.query(SQL)
        users = []
        for c in res:
            users.append(User(id=c[0], name=c[1], surname=c[2]))
        return users
    
    def query_users_by_pref(self, name_pref, surname_pref):
        SQL = "SELECT id, name, surname FROM users where name like '{}%' and surname like '{}%'".format(name_pref, surname_pref)
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
        
    def add_user_short(self, name, surname):
        SQL = "INSERT INTO users (name, surname) VALUES ('{}','{}')"
        SQL = SQL.format(name, surname)
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
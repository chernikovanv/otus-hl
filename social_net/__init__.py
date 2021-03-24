from flask import Flask
from social_net.db import init_db, close_db

app = Flask(__name__)

#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    close_db()

#init_db()

import social_net.api

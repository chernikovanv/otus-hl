from social_net import app

@app.route('/hello')
def hello():
    return 'Hello world!'

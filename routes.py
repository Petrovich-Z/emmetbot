from app import app

@app.route('/index')
@app.route('/')
def hello_world():
    return 'Hello World!'
from flask import Flask

#pip install https://github.com/mitsuhiko/flask/tarball/master 
app = Flask(__name__)
print(__name__)

@app.route('/')
def hello_world():
	return 'hello, keyboard'
	
@app.route('/hello')
def hello():
	return 'we could get it!!'
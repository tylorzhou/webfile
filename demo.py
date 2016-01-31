import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import logging
from logging.handlers import RotatingFileHandler

	 
app = Flask(__name__)
app.config.from_object(__name__)
handler = RotatingFileHandler('demodebug.log', maxBytes = 10000, backupCount = 1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

#print(app.root_path)
#print(app.instance_path)
 
app.config.update(dict(
		DATABASE=os.path.join(app.root_path, 'flask.db'),
		SECRET_KEY = 'development key',
		USERNAME = 'admin',
		PASSWORD = 'default'
		))
app.config.from_envvar('FLASKR_SETTINGS', silent = True)


def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	app.logger.info("connect db")
	return rv
	
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
     
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        app.logger.info('closed db')
        
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

    
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print ('initialized the database')
    
@app.route('/add', methods = ['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title, text) values (?, ?)',
				[request.form['title'], request.form['text']])
	db.commit()
	flash('New entry was successfully posted')
	app.logger.info('added new entry')
	return redirect(url_for('show_entries'))
	
	
@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries = entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'invalid account'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'invalid password'
			app.logger.error('invalid password for user %s', app.config['USERNAME'])
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
		
	return render_template('login.html', error = error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	app.logger.warning('user %s logout' ,app.config['USERNAME'])
	return redirect(url_for('show_entries'))
	

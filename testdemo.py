import os
import demo
import unittest
import tempfile

class demoTestcase(unittest.TestCase):

	def setUp(self):
		print('setup invoked')
		self.db_fd, demo.app.config['DATABASE'] = tempfile.mkstemp()
		demo.app.config['TESTING'] = True
		self.app = demo.app.test_client()
		with demo.app.app_context():
			demo.init_db()
	
	def tearDown(self):
		print('teardown invoked')
		os.close(self.db_fd)
		os.unlink(demo.app.config['DATABASE'])
		
	def test_empty_db(self):
		print('testdb invoked')
		rv = self.app.get('/')
		assert b'No entries here so far' in rv.data
		
	def test_Loginout(self):
		print('test_loginout invoked')
		rv = self.login('admin', 'default')
		assert b'You were logged in' in rv.data
		rv = self.logout('test2', 'user2')
		assert b'You were logged out' in rv.data
		rv = self.login('1admin', 'default')
		assert b'invalid account' in rv.data
		
	
	def login(self, username, password):
		return self.app.post('/login', data = dict(
				username = username, password = password), follow_redirects = True)
	
	def logout(self, username, password):
		return self.app.get('/logout', follow_redirects = True)
	

		

if __name__ == '__main__':
	unittest.main()
	
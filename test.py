import os
from TcTube import main
import unittest

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
    def test_index(self):
        response = self.app.get('/', follow_redirects = True)
        self.assertEquals(response.status, "200 OK")
    def test_login(self):
         response = self.app.post('/login', data = {
            'account': 'test',
            'password': "test"
        }, follow_redirects = True)
        # Assert response is 200 OK.
        self.assertEquals(response.status, "200 OK")
if __name__ == '__main__':
    unittest.main()
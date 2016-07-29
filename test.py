import os
import unittest
import tempfile
import webtest

import main
class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
    def test_redirect(self):
        response = self.app.get('/')
        self.assertEquals(response.status, "302 FOUND")
    def test_login_logout(self):
        # response = self.app.get('/login')
        # response = self.app.post('/login/', follow_redirects = True)
        response = self.app.post('/login/', data = {
            'account': 'test',
            'password': "test",
            'submit': "登入"
        }, follow_redirects = True)
        self.assertEquals(response.status, "200 OK")
        response = self.app.get('/')
        self.assertEquals(response.status, "200 OK")
        response = self.app.post('/logout/', data = {
            next: "/"
        }, follow_redirects = True)
        self.assertEquals(response.status, "200 OK")


if __name__ == '__main__':
    unittest.main()
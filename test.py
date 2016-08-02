import unittest

import main

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        main.flaskApplication.config['TESTING'] = True
        self.flaskApplication = main.flaskApplication.test_client()
    def test_login_redirect(self):
        response = self.flaskApplication.get('/')
        self.assertEquals(response.status, "302 FOUND")
    def test_login_logout(self):
        response = self.flaskApplication.post('/login/', data = {
            'account': 'test',
            'password': "test",
            'submit': "登入"
        }, follow_redirects = True)
        self.assertEquals(response.status, "200 OK")
        response = self.flaskApplication.get('/')
        self.assertEquals(response.status, "200 OK")
        response = self.flaskApplication.post('/logout/', data = {
            next: "/"
        }, follow_redirects = True)
        self.assertEquals(response.status, "200 OK")


if __name__ == '__main__':
    unittest.main()
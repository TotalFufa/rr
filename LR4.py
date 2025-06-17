import os
import unittest
from flask import session
from app import app, hash_password, user_exists, register_user, verify_user
class TestAuthApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        if os.path.exists('users.txt'):
            os.remove('users.txt')
    def tearDown(self):
        if os.path.exists('users.txt'):
            os.remove('users.txt')
    def test_hash_password(self):
        self.assertEqual(
            hash_password('test123'),
            'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae'
        )
        self.assertNotEqual(
            hash_password('test123'),
            hash_password('different')
        )
    def test_user_exists(self):
        self.assertFalse(user_exists('testuser'))
        register_user('testuser', 'testpass')
        self.assertTrue(user_exists('testuser'))
        self.assertFalse(user_exists('nonexistent'))
    def test_register_user(self):
        register_user('newuser', 'newpass')
        with open('users.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('newuser:', content)
            self.assertNotIn('newpass', content)
    def test_verify_user(self):
        register_user('validuser', 'validpass')
        self.assertTrue(verify_user('validuser', 'validpass'))
        self.assertFalse(verify_user('validuser', 'wrongpass'))
        self.assertFalse(verify_user('nonexistent', 'anypass'))
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('Войти', response_text)
        self.assertIn('Зарегистрироваться', response_text)
        register_user('homeuser', 'homepass')
        with self.client:
            self.client.post('/login', data={
                'username': 'homeuser',
                'password': 'homepass'
            })
            response = self.client.get('/')
            response_text = response.get_data(as_text=True)
            self.assertIn('homeuser', response_text)
            self.assertIn('Выйти', response_text)
    def test_login(self):
        register_user('loginuser', 'loginpass')
        with self.client:
            response = self.client.post('/login', data={
                'username': 'loginuser',
                'password': 'loginpass'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            response_text = response.get_data(as_text=True)
            self.assertIn('Привет, loginuser', response_text)
            self.assertIn('Выйти', response_text)
            self.assertEqual(session['username'], 'loginuser')
        with self.client:
            with self.client.session_transaction() as sess:
                sess.clear()
            response = self.client.post('/login', data={
                'username': 'loginuser',
                'password': 'wrongpass'
            }, follow_redirects=True)
            response_text = response.get_data(as_text=True)
            self.assertIn('Неверное имя пользователя или пароль', response_text)
            with self.client.session_transaction() as sess:
                self.assertNotIn('username', sess)
    def test_register_route(self):
        response = self.client.post('/register', data={
            'username': 'newreguser',
            'password': 'newregpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('Регистрация прошла успешно', response_text)
        response = self.client.post('/register', data={
            'username': 'newreguser',
            'password': 'newregpass'
        }, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertIn('Пользователь с таким именем уже существует', response_text)
    def test_logout(self):
        register_user('logoutuser', 'logoutpass')
        with self.client:
            self.client.post('/login', data={
                'username': 'logoutuser',
                'password': 'logoutpass'
            })
            self.assertEqual(session['username'], 'logoutuser')
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            response_text = response.get_data(as_text=True)
            self.assertNotIn('username', session)
            self.assertIn('Войти', response_text)
if __name__ == '__main__':
    unittest.main()
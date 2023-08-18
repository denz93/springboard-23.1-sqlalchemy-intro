from unittest import TestCase
from app import create_app, db, User
from bs4 import BeautifulSoup
from config import TestingConfig

class UserUnitTest(TestCase):
    def setUp(self) -> None:
      self.app = create_app(TestingConfig)
    def tearDown(self) -> None:
      with self.app.app_context():
        db.session.remove()
        db.drop_all()
    
    def test_home_page(self):
        with self.app.test_client() as client:
          res = client.get('/', follow_redirects=False)
          self.assertEqual(res.status_code, 302)
          self.assertTrue(res.location.endswith('/users'))

    def test_users_page(self):
        with self.app.test_client() as client:
          res = client.get('/users')
          
          self.assertEqual(res.status_code, 200)
          root = BeautifulSoup(res.data, 'html.parser')
          ul = root.find('ul')
          self.assertIsNotNone(ul)
          self.assertEqual(len(ul.findChildren('li')), 0)

        #Insert some test users
        with self.app.app_context():
          user1 = User(first_name='Alex', last_name='Hoang', image_url=None)
          user2 = User(first_name='Elsa', last_name='Luis', image_url='htpps://notreal.com/img.png')
          db.session.add(user1)
          db.session.add(user2)
          db.session.commit()

        with self.app.test_client() as client:
          res = client.get('/users')
          self.assertEqual(res.status_code, 200)
          root = BeautifulSoup(res.data, 'html.parser')
          ul = root.find('ul')
          self.assertIsNotNone(ul)
          self.assertEqual(len(ul.findChildren('li')), 2)
          lis = ul.findChildren('li')
          
          self.assertEqual(lis[0].find('a').get_text(), 'Alex Hoang')
          self.assertEqual(lis[1].find('a').get_text(), 'Elsa Luis')

    def test_create_user(self):
      with self.app.test_client() as client:
        form_data = { "first_name": "Alex", "last_name": "Hoang" }
        res = client.post('/users/new', data=form_data, follow_redirects=True)

        root = BeautifulSoup(res.data, 'html.parser')
        ul = root.find('ul')

        self.assertIsNotNone(ul)
        self.assertEqual(ul.findChild('li').findChild('a').get_text(), 'Alex Hoang')
    def test_update_user(self):
      with self.app.app_context():
        user = User(first_name='Alex', last_name = 'Hoang')
        db.session.add(user)
        db.session.commit()

      with self.app.test_client() as client:
          form_data = {"last_name": "Luis", "image_url": "https://noresource.com/img.png" }
          res = client.post('/users/1/edit', data=form_data, follow_redirects=True)
          # self.assertTrue(res.location.endswith('/users/1'))
          root = BeautifulSoup(res.data, 'html.parser')
          img = root.find('img')
          name = root.select_one('div div:nth-child(2) div:nth-child(1)')

          self.assertIsNotNone(img)
          self.assertIsNotNone(name)

          self.assertEqual(img.get('src'), 'https://noresource.com/img.png')
          self.assertEqual(name.get_text(), 'Alex Luis')
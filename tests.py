import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import DogUser, Post


class DogUserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        d = DogUser(dog_name='groshyk')
        d.set_password('groshyk')
        self.assertFalse(d.check_password('whong_password'))
        self.assertTrue(d.check_password('groshyk'))

    # def test_avatar(self):
    #     d = DogUser(dog_name='groshyk', email='groshyk@gmail.com')
    #     self.assertEqual(d.avatar(128), ('https://www.gravatar.com/avatar/'
    #                                      'd4c74594d841139328695756648b6bd6'
    #                                      '?d=identicon&s=128'))

    def test_follow(self):
        d1 = DogUser(dog_name='groshyk', email='groshyk@gmail.com')
        d2 = DogUser(dog_name='shkedryk', email='shkedryk@gmail.com')
        db.session.add(d1)
        db.session.add(d2)
        db.session.commit()
        self.assertEqual(d1.followed.all(), [])
        self.assertEqual(d1.followers.all(), [])

        d1.follow(d2)
        db.session.commit()
        self.assertTrue(d1.is_following(d2))
        self.assertEqual(d1.followed.count(), 1)
        self.assertEqual(d1.followed.first().dog_name, 'shkedryk')
        self.assertEqual(d2.followers.count(), 1)
        self.assertEqual(d2.followers.first().dog_name, 'groshyk')

        d1.unfollow(d2)
        db.session.commit()
        self.assertFalse(d1.is_following(d2))
        self.assertEqual(d1.followed.count(), 0)
        self.assertEqual(d2.followers.count(), 0)

    def test_follow_posts(self):
        # create 4 dog_users
        d1 = DogUser(dog_name='groshyk', email='groshyk@gmail.com')
        d2 = DogUser(dog_name='shkedryk', email='shkedryk@gmail.com')
        d3 = DogUser(dog_name='gryven', email='gryven@gmail.com')
        d4 = DogUser(dog_name='ivan', email='ivan@gmail.com')
        db.session.add_all([d1, d2, d3, d4])

        # create 4 posts
        now = datetime.utcnow()
        p1 = Post(body="post from groshyk", author=d1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from shkedryk", author=d2,
                  timestamp=now + timedelta(seconds=1))
        p3 = Post(body="post from gryven", author=d3,
                  timestamp=now + timedelta(seconds=1))
        p4 = Post(body="post from ivan", author=d4,
                  timestamp=now + timedelta(seconds=1))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        d1.follow(d2)  # groshyk follows shkedryk
        d1.follow(d4)  # groshyk follows ivan
        d2.follow(d3)  # shkedryk follows gryven
        d3.follow(d4)  # gryven follows ivan
        db.session.commit()

        # check the followed posts of each dog_user
        f1 = d1.followed_posts().all()
        f2 = d2.followed_posts().all()
        f3 = d3.followed_posts().all()
        f4 = d4.followed_posts().all()
        self.assertEqual(f1, [p1, p2, p4])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
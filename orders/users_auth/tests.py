from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):

    def test_create_user(self):
        usr = get_user_model()
        user = usr.objects.create_user(email='normal@user.com', password='foo', username='normal@user123.')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertRegex(user.username, expected_regex=r'^[\w.@+-]+$')

        with self.assertRaises(TypeError):
            usr.objects.create_user()
        with self.assertRaises(TypeError):
            usr.objects.create_user(email='')
        with self.assertRaises(ValueError):
            usr.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        usr = get_user_model()
        admin_user = usr.objects.create_superuser(email='super@user.com', password='foo', username='super@user123.')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertFalse(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertRegex(admin_user.username, expected_regex=r'^[\w.@+-]+$')

        with self.assertRaises(ValueError):
            usr.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken import models
from users_auth.views import *
from users_auth.models import *

  
class TestSetUP(APITestCase):

    def setUp(self) -> None:
        self.login_url = reverse('user_login')
        self.email_confirmation_url = reverse('user_confirmation')
        self.details_url = 'http://127.0.0.1:8000/api/v1/user/details/'
        self.register_url = 'http://127.0.0.1:8000/api/v1/user/register/'
        self.reg_user_data = {
                                'first_name': 'Иван',
                                'last_name': 'Иванов',
                                'email': 'ivanov@mail.ru',
                                'password': 'Ivanov1234',
                                'company': 'Company',
                                'position': 'manager'
                             }
        self.credentials = {"email": "ivanov@mail.ru", "password": "Ivanov1234"}
        self.confirm_token = get_token_generator().generate_token()
        self.auth_token = Token.generate_key()
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()


class TestViews(TestSetUP):

    def test_user_register(self):
        resp = self.client.post(self.register_url, self.reg_user_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().first_name, self.reg_user_data['first_name'])
        self.assertEqual(User.objects.get().last_name, self.reg_user_data['last_name'])
        self.assertEqual(User.objects.get().email, self.reg_user_data['email'])
        self.assertEqual(User.objects.get().company, self.reg_user_data['company'])
        self.assertEqual(User.objects.get().position, self.reg_user_data['position'])
        self.assertEqual(User.objects.get().type, 'buyer')

    def test_user_email_confirmation(self):
        user = User.objects.create_user(**self.credentials)
        token_obj = ConfirmEmailToken.objects.create(key=self.confirm_token, user_id=user.id)

        resp = self.client.post(self.email_confirmation_url, data={
            'email': user.email,
            'token': token_obj.key}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.first().is_active, True)
        self.assertIsNone(ConfirmEmailToken.objects.first())
        
     
    def test_user_login(self):
        User.objects.create_user(**self.credentials, is_active=True)

        resp = self.client.post(self.login_url, self.credentials, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['Token'])

    def test_user_details(self):
        user = User.objects.create_user(**self.credentials, is_active=True)
        Token.objects.create(key=self.auth_token, user_id=user.id)

        resp_get = self.client.get(self.details_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        resp_retrieve = self.client.get(self.details_url + str(user.id) + '/',
                                         headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        resp_post = self.client.post(self.details_url + str(user.id) + '/' + 'change/', data={'password': 'Ivanov1234NEW'},
                                      headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_retrieve.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_post.status_code, status.HTTP_200_OK)

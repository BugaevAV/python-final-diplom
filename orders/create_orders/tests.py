from django.urls import reverse
from django.db.models import Q, F, Sum
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from create_orders.views import *
from create_orders.models import *
from ordering_goods.tasks import price_loader
import ujson


class TestSetUP(APITestCase):

    def setUp(self) -> None:
        
        self.order_url = reverse('order')
        self.basket_url = reverse('basket')
        self.orders_url = reverse('partner_orders')
        self.state_url = 'http://127.0.0.1:8000/api/v1/partner/state/'
        self.contact_url = 'http://127.0.0.1:8000/api/v1/user/contact/'
        self.price_url = 'https://raw.githubusercontent.com/BugaevAV/python-final-diplom/vers_1/data/shop1.yaml'
        self.auth_token = Token.generate_key()
        self.credentials = {"email": "ivanov@mail.ru", "password": "Ivanov1234"}
        self.user = User.objects.create_user(**self.credentials, is_active=True, type='shop')
        Token.objects.create(key=self.auth_token, user_id=self.user.id)
        self.contacts_data = {
                                "city": "Санкт-Петербург",
                                "street": "Комендантский проспект",
                                "house": "21",
                                "building": "2",
                                "apartment": "229",
                                "phone": "+7 900 800 70 60"
                             }
        self.items = {'items': r'[{"product_info": 1, "quantity": 5}, {"product_info": 2, "quantity": 6}]'}
        price_loader(self.price_url, self.user.id)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()


class TestViews(TestSetUP):

    def test_contacts(self):
        resp_post = self.client.post(self.contact_url, data=self.contacts_data,
                                      headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.get().city, self.contacts_data['city'])
        self.assertEqual(Contact.objects.get().street, self.contacts_data['street'])
        self.assertEqual(Contact.objects.get().house, self.contacts_data['house'])
        self.assertEqual(Contact.objects.get().building, self.contacts_data['building'])
        self.assertEqual(Contact.objects.get().apartment, self.contacts_data['apartment'])
        self.assertEqual(Contact.objects.get().phone, self.contacts_data['phone'])
        
        resp_get_list = self.client.get(self.contact_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_get_list.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_get_list.data.get('count'))

        resp_retrieve = self.client.get(self.contact_url + str(self.user.id) + '/',
                                         headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_retrieve.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_retrieve.data.get('user'), self.user.id)

        resp_patch = self.client.patch(self.contact_url + str(self.user.id) + '/', data={'street': 'Невский проспект'},
                                       headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(Contact.objects.get().street, 'Невский проспект')

        resp_delete = self.client.delete(self.contact_url + str(self.user.id) + '/',
                                         headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)


    def test_basket(self):
        resp_post = self.client.post(self.basket_url, data=self.items,
                                      headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.filter(id=1).get().quantity , 5)
        self.assertEqual(OrderItem.objects.filter(id=2).get().quantity , 6)
        self.assertEqual(Order.objects.get().state, 'basket')
        
        quantities = [int(item['quantity']) for item in OrderItem.objects.values('quantity')]
        prices = [int(item['price']) for item in ProductInfo.objects.filter(id__in=[1, 2]).values('price')]
        resp_get = self.client.get(self.basket_url,
                                    headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(sum([a*b for a, b in zip(quantities, prices)]), resp_get.data[0].get('total_sum'))
     
        resp_put = self.client.put(self.basket_url, data={'items': r'[{"id": 1, "quantity": 10}]'},
                                   headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        self.assertEqual(OrderItem.objects.filter(id=1).get().quantity , 10)

        resp_delete = self.client.delete(self.basket_url, data={'items': '1,2'},
                                   headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OrderItem.objects.filter(id__in=[1, 2]))       


    def test_order(self):
        order = Order.objects.create(user_id=self.user.id, state='basket')
        OrderItem.objects.create(order_id=order.id, product_info_id=9, quantity=10)
        contact = Contact.objects.create(user_id= self.user.id, **self.contacts_data)

        resp_post = self.client.post(self.order_url, data={"order_id": "2", "contact": contact.id},
                                      headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get().state, 'new')
        self.assertTrue(Order.objects.values('contact_id'))

        quantities = [int(item['quantity']) for item in OrderItem.objects.values('quantity')]
        prices = [int(item['price']) for item in ProductInfo.objects.filter(id=9).values('price')]
        resp_get = self.client.get(self.order_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertEqual(sum([a*b for a, b in zip(quantities, prices)]), resp_get.data[0].get('total_sum'))

    def test_partner_state(self):
        resp_get = self.client.get(self.state_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_get.data[0].get('state'))
        
        resp_post = self.client.post(self.state_url, headers={'Authorization': f'Token {self.auth_token}'},
                                     data={'state': 'off'}, format='json')
        self.assertEqual(resp_post.status_code, status.HTTP_200_OK)
        self.assertFalse(Shop.objects.get().state)

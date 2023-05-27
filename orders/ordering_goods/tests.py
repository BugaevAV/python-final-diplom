from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ordering_goods.views import *
from ordering_goods.tasks import price_loader


class TestSetUP(APITestCase):

    def setUp(self) -> None:
        
        self.categories_url = reverse('categories')
        self.shops_url = reverse('shops')
        self.products_url = reverse('products')
        self.price_update_url = reverse('update_price')
        self.price_url = 'https://raw.githubusercontent.com/BugaevAV/python-final-diplom/vers_1/data/shop1.yaml'
        self.auth_token = Token.generate_key()
        self.credentials = {"email": "ivanov@mail.ru", "password": "Ivanov1234"}
        self.user = User.objects.create_user(**self.credentials, is_active=True)
        Token.objects.create(key=self.auth_token, user_id=self.user.id)
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()


class TestViews(TestSetUP):

    def test_get_categories(self):
        Category.objects.create(id='1', name='накопители')
        resp = self.client.get(self.categories_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Category.objects.get().name, 'накопители')

    def test_get_shops(self):
        Shop.objects.create(name='Связной')
        resp = self.client.get(self.shops_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Shop.objects.get().name, 'Связной')
    
    def test_get_products_info(self):
        Product.objects.create(name='Смартфон Apple iPhone XS Max 512GB (золотистый)', category_id='224')
        Category.objects.create(id='224', name='Смартфоны')
        resp = self.client.get(self.products_url, headers={'Authorization': f'Token {self.auth_token}'}, format='json')
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get().name, 'Смартфон Apple iPhone XS Max 512GB (золотистый)')
    
    def test_only_shops(self):
        resp = self.client.post(self.price_update_url, headers={'Authorization': f'Token {self.auth_token}'},
                                data={'url': self.price_url}, format='json')        
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_price_update(self):
        self.user.type = 'shop'
        self.user.save()
        resp = self.client.post(self.price_update_url, headers={'Authorization': f'Token {self.auth_token}'},
                                data={'url': self.price_url}, format='json')
        price_loader(self.price_url, self.user.id)
    
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Shop.objects.get().name, 'Связной')
        self.assertEqual(Category.objects.first().name, 'Смартфоны')
        self.assertEqual(Product.objects.first().name, 'Смартфон Apple iPhone XS Max 512GB (золотистый)')
        self.assertEqual(ProductInfo.objects.first().model, 'apple/iphone/xs-max')

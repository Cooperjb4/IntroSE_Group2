from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Product, Cart
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

class StoreTests(TestCase):
    def setUp(self):
        # sets up test data values
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.seller_group, created = Group.objects.get_or_create(name='Seller')
        self.user.groups.add(self.seller_group)

        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=Decimal('19.99'),
            stock=10,
            seller=self.user,
            image=self.test_image
        )

        self.client = Client()

    def test_signup(self):
        # test successful and failing signup tests
        url = reverse('signup')
        
        signup_data = {
            'username': 'newuser',
            'password': 'newpass123',
            'role': 'Seller'
        }
        response = self.client.post(url, signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        response = self.client.post(url, signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already exists')
        # updates username and password for test
        signup_data['username'] = 'anotheruser'
        signup_data['password'] = 'short'
        response = self.client.post(url, signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password must be at least 8 characters')

    def test_login(self):
        # tests login scenarios for wrong password and username
        url = reverse('login')

        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, 302)

        login_data['password'] = 'wrongpass'
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

        login_data['username'] = 'nonexistent'
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_add_to_cart(self):
        # tests adding product to cart

        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)

        cart_item = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.quantity, 1)

        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_view_account(self):
        # tests the account page
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Seller')

    def test_add_product(self):
        # tests product posting
        
        self.client.login(username='testuser', password='testpass123')

        image = SimpleUploadedFile(
            name='new_product.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        product_data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '29.99',
            'stock': '5',
            'image': image
        }
        response = self.client.post(reverse('add_product'), product_data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Product.objects.filter(name='New Product').exists())
        new_product = Product.objects.get(name='New Product')
        self.assertEqual(new_product.seller, self.user)
        self.assertEqual(new_product.price, Decimal('29.99'))

        product_data['price'] = '-10.00'
        response = self.client.post(reverse('add_product'), product_data)
        self.assertEqual(response.status_code, 302)

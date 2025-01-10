from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from .views import RegisterApiView, VerifyApiView
from .models import OTP
from .serializers import UserSerializer, OtpSerializer

User = get_user_model()

class RegisterApiViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RegisterApiView.as_view({'post':'create'})
        self.url = '/register/'
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
        }

    def test_user_registration(self):
        request = self.factory.post(self.url, self.user_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.email, self.user_data['email'])

        otp = OTP.objects.filter(user=user).first()
        self.assertIsNotNone(otp)
        self.assertEqual(otp.user, user)

    def test_user_registration_invalid_data(self):
        invalid_data = {
            'password': 'testpassword123',
            'email': 'smth',
        }
        request = self.factory.post(self.url, invalid_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)

    def test_register_existing_email(self):
        User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
        )

        request = self.factory.post(self.url, self.user_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)


class VerifyApiViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = VerifyApiView.as_view()
        self.url = '/verify/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            is_verified=False,
        )
        self.otp = OTP.objects.create(
            user=self.user,
            otp_code='123456',  
        )

    def test_otp_verification_success(self):
        otp_data = {
            'email': 'test@example.com',
            'otp': '123456',
        }
        request = self.factory.post(self.url, otp_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_otp_verification_invalid_otp(self):
        invalid_otp_data = {
            'email': 'test@example.com',
            'otp': '654321',  
        }
        request = self.factory.post(self.url, invalid_otp_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)

    def test_otp_verification_invalid_email(self):
        invalid_email_data = {
            'email': 'nonexistent@example.com',
            'otp_code': '123456',
        }
        request = self.factory.post(self.url, invalid_email_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)

    def test_verify_already_verified_user(self):
        self.user.is_verified = True
        self.user.save()

        otp_data = {
            'email': 'test@example.com',
            'otp': '123456',
        }
        request = self.factory.post(self.url, otp_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, 400)

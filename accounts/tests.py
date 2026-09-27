from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Skill, Follow, ConnectionRequest

class AuthenticationAndAccountTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.profile_url = reverse('current_user_profile')
        self.developer_list_url = reverse('developer_list')
        self.skill = Skill.objects.create(name='Django', category='BACKEND')

        self.user_data = {
            'username': 'john_developer',
            'email': 'john@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
            'role': 'DEVELOPER',
            'headline': 'Full Stack Developer',
            'location': 'New York, NY'
        }
        self.user = User.objects.create_user(
            username='jane_dev',
            email='jane@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], self.user_data['email'])

    def test_user_registration_password_mismatch(self):
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)

    def test_jwt_login_success(self):
        response = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'StrongPassword123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'jane_dev')

    def test_jwt_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'WrongPassword!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_profile_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_unauthenticated_profile_access_denied(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_follow_toggle_flow(self):
        target_user = User.objects.create_user(
            username='target_dev',
            email='target@example.com',
            password='StrongPassword123!'
        )
        self.client.force_authenticate(user=self.user)

        follow_url = reverse('follow_toggle', kwargs={'username': target_user.username})
        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_following'])
        self.assertEqual(response.data['followers_count'], 1)

        response2 = self.client.post(follow_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data['is_following'])
        self.assertEqual(response2.data['followers_count'], 0)

    def test_cannot_follow_self(self):
        self.client.force_authenticate(user=self.user)
        follow_url = reverse('follow_toggle', kwargs={'username': self.user.username})
        response = self.client.post(follow_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_connection_request_lifecycle(self):
        other_user = User.objects.create_user(
            username='recruiter_bob',
            email='bob@recruiter.com',
            password='StrongPassword123!',
            role='RECRUITER'
        )
        self.client.force_authenticate(user=self.user)

        conn_url = reverse('connections_list_create')
        res_send = self.client.post(conn_url, {
            'receiver': other_user.id,
            'message': 'Looking forward to connecting.'
        }, format='json')
        self.assertEqual(res_send.status_code, status.HTTP_201_CREATED)
        conn_id = res_send.data['id']

        self.client.force_authenticate(user=other_user)
        action_url = reverse('connection_action', kwargs={'pk': conn_id, 'action': 'accept'})
        res_action = self.client.post(action_url)
        self.assertEqual(res_action.status_code, status.HTTP_200_OK)
        self.assertEqual(res_action.data['status'], 'ACCEPTED')

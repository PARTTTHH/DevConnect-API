from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, Follow
from .models import Post, PostLike, PostComment


class PostAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='dave_backend',
            email='dave@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )
        self.follower_user = User.objects.create_user(
            username='emily_coder',
            email='emily@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )
        self.stranger_user = User.objects.create_user(
            username='stranger_bob',
            email='stranger@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )

        Follow.objects.create(follower=self.follower_user, following=self.author)

        self.post = Post.objects.create(
            author=self.author,
            content='Tip of the day: Use select_related in Django.',
            code_snippet='users = User.objects.all()',
            code_language='python'
        )
        self.list_url = reverse('post_list_create')
        self.feed_url = reverse('post_feed')

    def test_global_post_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_personalized_feed_shows_followed_posts(self):
        self.client.force_authenticate(user=self.follower_user)
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_personalized_feed_excludes_unfollowed_posts(self):
        self.client.force_authenticate(user=self.stranger_user)
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.author)
        payload = {
            'content': 'Check out this quick utility helper:',
            'code_snippet': 'const debounce = () => {}',
            'code_language': 'javascript'
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code_language'], 'javascript')

    def test_post_like_toggle(self):
        self.client.force_authenticate(user=self.follower_user)
        like_url = reverse('post_like_toggle', kwargs={'pk': self.post.id})

        res1 = self.client.post(like_url)
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res1.data['is_liked'])
        self.assertEqual(res1.data['likes_count'], 1)

        res2 = self.client.post(like_url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res2.data['is_liked'])
        self.assertEqual(res2.data['likes_count'], 0)

    def test_post_comment_flow(self):
        self.client.force_authenticate(user=self.follower_user)
        comment_url = reverse('post_comments_list_create', kwargs={'pk': self.post.id})
        res = self.client.post(comment_url, {'content': 'Great tip!'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.post.refresh_from_db()
        self.assertEqual(self.post.comments_count, 1)

    def test_non_author_cannot_delete_post(self):
        self.client.force_authenticate(user=self.stranger_user)
        detail_url = reverse('post_detail', kwargs={'pk': self.post.id})
        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


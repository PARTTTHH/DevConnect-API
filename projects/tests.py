from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, Skill
from .models import Project, ProjectStar, ProjectComment

class ProjectAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='alice_dev',
            email='alice@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )
        self.other_user = User.objects.create_user(
            username='charlie_dev',
            email='charlie@example.com',
            password='StrongPassword123!',
            role='DEVELOPER'
        )
        self.skill_django = Skill.objects.create(name='Django', category='BACKEND')
        self.skill_react = Skill.objects.create(name='React', category='FRONTEND')

        self.project = Project.objects.create(
            owner=self.owner,
            title='Realtime Chat Engine',
            tagline='WebSockets powered realtime chat system',
            description='High performance scalable chat system built with Django Channels and Redis.',
            repo_url='https://github.com/alice/realtime-chat',
            github_repo_name='alice/realtime-chat',
            demo_url='https://chat.alice.dev',
            project_type='API',
            tags=['django', 'websockets', 'redis'],
            stars_count=10
        )
        self.project.tech_stack.add(self.skill_django)
        self.list_url = reverse('project_list_create')

    def test_project_list_pagination_structure(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_project_conditional_filtering_by_skill(self):
        response = self.client.get(f'{self.list_url}?skill=Django')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response_empty = self.client.get(f'{self.list_url}?skill=React')
        self.assertEqual(response_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_empty.data['results']), 0)

    def test_project_lookup_search(self):
        response = self.client.get(f'{self.list_url}?search=WebSockets')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Realtime Chat Engine')

    def test_project_create_authenticated(self):
        self.client.force_authenticate(user=self.owner)
        payload = {
            'title': 'AI Code Reviewer',
            'tagline': 'Automated PR code reviewer with LLM',
            'description': 'Analyzes pull requests using LLM prompt engineering.',
            'repo_url': 'https://github.com/alice/ai-reviewer',
            'github_repo_name': 'alice/ai-reviewer',
            'project_type': 'AI_ML',
            'tags': ['python', 'ai', 'openai']
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'AI Code Reviewer')

    def test_project_create_unauthenticated_denied(self):
        payload = {'title': 'Unauthorized Project', 'description': 'desc', 'repo_url': 'https://github.com'}
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_project_owner_update_allowed(self):
        self.client.force_authenticate(user=self.owner)
        detail_url = reverse('project_detail', kwargs={'slug': self.project.slug})
        response = self.client.patch(detail_url, {'tagline': 'Updated Tagline'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.tagline, 'Updated Tagline')

    def test_project_non_owner_update_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        detail_url = reverse('project_detail', kwargs={'slug': self.project.slug})
        response = self.client.patch(detail_url, {'tagline': 'Hacked Tagline'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_star_toggle(self):
        self.client.force_authenticate(user=self.other_user)
        star_url = reverse('project_star_toggle', kwargs={'slug': self.project.slug})

        response = self.client.post(star_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_starred'])
        self.assertEqual(response.data['stars_count'], 11)

        response2 = self.client.post(star_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertFalse(response2.data['is_starred'])
        self.assertEqual(response2.data['stars_count'], 10)

    def test_project_comment_flow(self):
        self.client.force_authenticate(user=self.other_user)
        comment_url = reverse('project_comments_list_create', kwargs={'slug': self.project.slug})
        response = self.client.post(comment_url, {'content': 'Awesome project architecture!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjectComment.objects.filter(project=self.project).count(), 1)

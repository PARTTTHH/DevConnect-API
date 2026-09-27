from django.core.management.base import BaseCommand
from accounts.models import User, Skill, Follow, ConnectionRequest
from projects.models import Project, ProjectStar, ProjectComment
from posts.models import Post, PostLike, PostComment
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Seeds the database with realistic sample developers, skills, projects, and posts.'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing mock data...')
        ProjectComment.objects.all().delete()
        ProjectStar.objects.all().delete()
        Project.objects.all().delete()
        PostComment.objects.all().delete()
        PostLike.objects.all().delete()
        Post.objects.all().delete()
        Follow.objects.all().delete()
        ConnectionRequest.objects.all().delete()
        Notification.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Skill.objects.all().delete()

        self.stdout.write('Seeding Skills...')
        skills_data = [
            ('Python', 'LANGUAGE'),
            ('JavaScript', 'LANGUAGE'),
            ('TypeScript', 'LANGUAGE'),
            ('Go', 'LANGUAGE'),
            ('Rust', 'LANGUAGE'),
            ('Django', 'BACKEND'),
            ('Django REST Framework', 'BACKEND'),
            ('FastAPI', 'BACKEND'),
            ('Node.js', 'BACKEND'),
            ('React', 'FRONTEND'),
            ('Next.js', 'FRONTEND'),
            ('Vue.js', 'FRONTEND'),
            ('PostgreSQL', 'DATABASE'),
            ('Redis', 'DATABASE'),
            ('Docker', 'DEVOPS'),
            ('Kubernetes', 'DEVOPS'),
            ('AWS', 'DEVOPS'),
            ('GraphQL', 'BACKEND'),
            ('PyTorch', 'AI_ML'),
            ('TailwindCSS', 'FRONTEND'),
        ]
        skill_objs = {}
        for name, cat in skills_data:
            s, _ = Skill.objects.get_or_create(name=name, defaults={'category': cat})
            skill_objs[name] = s

        self.stdout.write('Seeding Users...')
        dev1 = User.objects.create_user(
            username='parth_dev',
            email='parth@devconnect.io',
            password='Password123!',
            role='DEVELOPER',
            headline='Backend Architect & Distributed Systems Engineer',
            bio='Passionate about high-throughput REST APIs, PostgreSQL optimization, and scalable microservices.',
            location='San Francisco, CA',
            github_username='PARTTTHH',
            github_url='https://github.com/PARTTTHH',
            portfolio_url='https://parth.dev',
            linkedin_url='https://linkedin.com/in/parth',
            is_available_for_hire=True,
            is_verified=True,
        )
        dev1.skills.set([skill_objs['Python'], skill_objs['Django'], skill_objs['PostgreSQL'], skill_objs['Docker'], skill_objs['Redis']])

        dev2 = User.objects.create_user(
            username='sarah_frontend',
            email='sarah@devconnect.io',
            password='Password123!',
            role='DEVELOPER',
            headline='Senior Frontend Engineer | React & Next.js Enthusiast',
            bio='Building sleek, accessible, and high-performance design systems and web apps.',
            location='New York, NY',
            github_username='sarahcodes',
            github_url='https://github.com/sarahcodes',
            portfolio_url='https://sarah.design',
            is_available_for_hire=True,
            is_verified=True,
        )
        dev2.skills.set([skill_objs['JavaScript'], skill_objs['TypeScript'], skill_objs['React'], skill_objs['Next.js'], skill_objs['TailwindCSS']])

        dev3 = User.objects.create_user(
            username='alex_ml',
            email='alex@devconnect.io',
            password='Password123!',
            role='DEVELOPER',
            headline='AI Research Engineer | LLMs & PyTorch',
            bio='Working on generative models, vector search, and edge inference pipelines.',
            location='Austin, TX',
            github_username='alex-ai',
            github_url='https://github.com/alex-ai',
            is_available_for_hire=False,
            is_verified=False,
        )
        dev3.skills.set([skill_objs['Python'], skill_objs['PyTorch'], skill_objs['FastAPI'], skill_objs['Docker']])

        recruiter = User.objects.create_user(
            username='tech_recruiter_lisa',
            email='lisa@techventures.com',
            password='Password123!',
            role='RECRUITER',
            headline='Technical Talent Partner at TechVentures',
            bio='Hiring top backend, full-stack, and AI engineers globally.',
            location='Seattle, WA',
            linkedin_url='https://linkedin.com/in/lisa-recruiter',
            is_available_for_hire=False,
            is_verified=True,
        )

        self.stdout.write('Seeding Follows & Connections...')
        Follow.objects.create(follower=dev2, following=dev1)
        Follow.objects.create(follower=dev3, following=dev1)
        Follow.objects.create(follower=dev1, following=dev2)

        ConnectionRequest.objects.create(
            sender=recruiter,
            receiver=dev1,
            status='ACCEPTED',
            message='Hi Parth, love your backend projects! Would love to connect regarding senior opportunities.'
        )

        self.stdout.write('Seeding Projects & Repositories...')
        proj1 = Project.objects.create(
            owner=dev1,
            title='DevConnect API',
            tagline='Secure, Stateless REST Backend Ecosystem for Developers',
            description='A production-ready Django REST Framework API featuring JWT authentication, role-based access control, advanced PostgreSQL indexing and lookup search, and automated test coverage.',
            repo_url='https://github.com/PARTTTHH/DevConnect-API',
            github_repo_name='PARTTTHH/DevConnect-API',
            demo_url='https://api.devconnect.io/api/docs/',
            project_type='API',
            tags=['django', 'drf', 'jwt', 'postgresql', 'postman', 'rest-api'],
            stars_count=24,
            views_count=180,
            is_featured=True,
        )
        proj1.tech_stack.set([skill_objs['Python'], skill_objs['Django'], skill_objs['PostgreSQL'], skill_objs['Docker']])

        proj2 = Project.objects.create(
            owner=dev2,
            title='DevConnect Web UI',
            tagline='Next.js 14 Developer Community & Portfolio Platform',
            description='Modern, responsive frontend client for DevConnect built with Next.js App Router, Tailwind CSS, and TanStack Query.',
            repo_url='https://github.com/sarahcodes/devconnect-web',
            github_repo_name='sarahcodes/devconnect-web',
            demo_url='https://devconnect.io',
            project_type='WEB',
            tags=['nextjs', 'react', 'typescript', 'tailwindcss'],
            stars_count=18,
            views_count=95,
            is_featured=True,
        )
        proj2.tech_stack.set([skill_objs['React'], skill_objs['Next.js'], skill_objs['TypeScript'], skill_objs['TailwindCSS']])

        # Project stars and comments
        ProjectStar.objects.create(user=dev2, project=proj1)
        ProjectStar.objects.create(user=dev3, project=proj1)
        ProjectComment.objects.create(user=dev2, project=proj1, content='Super clean API architecture and Swagger docs! Loved the JWT flow.')

        self.stdout.write('Seeding Posts & Feed...')
        post1 = Post.objects.create(
            author=dev1,
            content='Just added role-based authorization and custom JWT claims to our API gateway. Here is how we enforce ownership:',
            code_snippet='''class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user''',
            code_language='python',
            likes_count=5,
            comments_count=1
        )
        PostLike.objects.create(user=dev2, post=post1)
        PostComment.objects.create(user=dev2, post=post1, content='Clean permission check pattern!')

        post2 = Post.objects.create(
            author=dev2,
            content='Loving TypeScript 5.4 release with new type narrowing helpers. Who else is using TS in all fullstack projects?',
            code_snippet='',
            code_language='',
            likes_count=3,
            comments_count=0
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded DevConnect API database!'))

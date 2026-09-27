from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'name': 'DevConnect API',
        'version': '1.0.0',
        'status': 'healthy',
        'documentation': {
            'swagger_ui': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'schema_json': request.build_absolute_uri('/api/schema/'),
        },
        'endpoints': {
            'auth_register': request.build_absolute_uri('/api/auth/register/'),
            'auth_login': request.build_absolute_uri('/api/auth/login/'),
            'auth_token_refresh': request.build_absolute_uri('/api/auth/token/refresh/'),
            'auth_me': request.build_absolute_uri('/api/auth/me/'),
            'developers': request.build_absolute_uri('/api/auth/developers/'),
            'skills': request.build_absolute_uri('/api/auth/skills/'),
            'projects': request.build_absolute_uri('/api/projects/'),
            'projects_trending': request.build_absolute_uri('/api/projects/trending/'),
            'posts_feed': request.build_absolute_uri('/api/posts/feed/'),
            'posts_global': request.build_absolute_uri('/api/posts/'),
            'notifications': request.build_absolute_uri('/api/notifications/'),
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    # API Root Overview
    path('api/', api_root, name='api_root'),

    # OpenAPI 3.0 Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Apps
    path('api/auth/', include('accounts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

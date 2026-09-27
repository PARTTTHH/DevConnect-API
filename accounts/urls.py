from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    CurrentUserProfileView,
    ChangePasswordView,
    DeveloperListView,
    DeveloperDetailView,
    FollowToggleView,
    FollowersListView,
    FollowingListView,
    SkillListCreateView,
    ConnectionRequestListCreateView,
    ConnectionRequestActionView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Profile & Skills
    path('me/', CurrentUserProfileView.as_view(), name='current_user_profile'),
    path('skills/', SkillListCreateView.as_view(), name='skills_list_create'),

    # Developer Profiles & Social graph
    path('developers/', DeveloperListView.as_view(), name='developer_list'),
    path('developers/<str:username>/', DeveloperDetailView.as_view(), name='developer_detail'),
    path('developers/<str:username>/follow/', FollowToggleView.as_view(), name='follow_toggle'),
    path('developers/<str:username>/followers/', FollowersListView.as_view(), name='followers_list'),
    path('developers/<str:username>/following/', FollowingListView.as_view(), name='following_list'),

    # Connection requests
    path('connections/', ConnectionRequestListCreateView.as_view(), name='connections_list_create'),
    path('connections/<int:pk>/<str:action>/', ConnectionRequestActionView.as_view(), name='connection_action'),
]

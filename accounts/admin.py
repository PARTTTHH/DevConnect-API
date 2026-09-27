from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Skill, Follow, ConnectionRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'headline', 'is_available_for_hire', 'is_verified', 'is_staff']
    list_filter = ['role', 'is_available_for_hire', 'is_verified', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('DevConnect Profile', {
            'fields': (
                'role', 'headline', 'bio', 'location', 'avatar_url',
                'github_username', 'github_url', 'portfolio_url',
                'linkedin_url', 'twitter_url', 'skills',
                'is_available_for_hire', 'is_verified'
            )
        }),
    )
    filter_horizontal = ('skills', 'groups', 'user_permissions')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['sender__username', 'receiver__username']

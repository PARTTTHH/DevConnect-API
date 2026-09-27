from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, Skill, Follow, ConnectionRequest


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims into the JWT payload
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['headline'] = user.headline
        token['avatar_url'] = user.avatar_url
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'headline': self.user.headline,
            'avatar_url': self.user.avatar_url,
        }
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'role', 'headline', 'bio', 'location']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    projects_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'headline', 'bio',
            'location', 'avatar_url', 'github_username', 'github_url',
            'portfolio_url', 'linkedin_url', 'twitter_url', 'skills',
            'is_available_for_hire', 'is_verified', 'followers_count',
            'following_count', 'projects_count', 'is_following', 'created_at'
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'headline', 'bio',
            'location', 'avatar_url', 'github_username', 'github_url',
            'portfolio_url', 'linkedin_url', 'twitter_url', 'skills',
            'is_available_for_hire'
        ]
        read_only_fields = ['id', 'email', 'role']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'New passwords do not match.'})
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    follower_avatar = serializers.CharField(source='follower.avatar_url', read_only=True)
    following_avatar = serializers.CharField(source='following.avatar_url', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'follower_username', 'follower_avatar', 'following', 'following_username', 'following_avatar', 'created_at']
        read_only_fields = ['follower']


class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender_detail = UserPublicSerializer(source='sender', read_only=True)
    receiver_detail = UserPublicSerializer(source='receiver', read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'sender', 'sender_detail', 'receiver', 'receiver_detail', 'status', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'sender', 'sender_detail', 'receiver_detail', 'status', 'created_at', 'updated_at']

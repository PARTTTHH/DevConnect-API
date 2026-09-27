from rest_framework import serializers
from .models import Post, PostLike, PostComment
from accounts.serializers import UserPublicSerializer


class PostCommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'post', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'post', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments = PostCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'code_snippet', 'code_language',
            'likes_count', 'comments_count', 'is_liked', 'comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'likes_count', 'comments_count', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False

    def create(self, validated_data):
        return Post.objects.create(author=self.context['request'].user, **validated_data)

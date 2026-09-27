from rest_framework import serializers
from .models import Project, ProjectStar, ProjectComment
from accounts.serializers import UserPublicSerializer, SkillSerializer
from accounts.models import Skill


class ProjectCommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = ProjectComment
        fields = ['id', 'user', 'project', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'project', 'created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    owner = UserPublicSerializer(read_only=True)
    tech_stack = SkillSerializer(many=True, read_only=True)
    is_starred = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'repo_url', 'github_repo_name',
            'demo_url', 'project_type', 'tech_stack', 'tags', 'stars_count',
            'views_count', 'is_featured', 'owner', 'is_starred', 'comments_count',
            'created_at', 'updated_at'
        ]

    def get_is_starred(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProjectStar.objects.filter(user=request.user, project=obj).exists()
        return False


class ProjectDetailSerializer(ProjectListSerializer):
    comments = ProjectCommentSerializer(many=True, read_only=True)

    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields + ['description', 'comments']


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    tech_stack_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), source='tech_stack', required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, default=list
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'tagline', 'description', 'repo_url', 'github_repo_name',
            'demo_url', 'project_type', 'tech_stack_ids', 'tags'
        ]
        read_only_fields = ['id', 'slug']

    def create(self, validated_data):
        tech_stack = validated_data.pop('tech_stack', [])
        project = Project.objects.create(owner=self.context['request'].user, **validated_data)
        if tech_stack:
            project.tech_stack.set(tech_stack)
        return project

    def update(self, instance, validated_data):
        tech_stack = validated_data.pop('tech_stack', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tech_stack is not None:
            instance.tech_stack.set(tech_stack)
        return instance

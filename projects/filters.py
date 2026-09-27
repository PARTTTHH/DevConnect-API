import django_filters
from .models import Project


class ProjectFilter(django_filters.FilterSet):
    min_stars = django_filters.NumberFilter(field_name='stars_count', lookup_expr='gte')
    max_stars = django_filters.NumberFilter(field_name='stars_count', lookup_expr='lte')
    project_type = django_filters.ChoiceFilter(choices=Project.PROJECT_TYPE_CHOICES)
    is_featured = django_filters.BooleanFilter()
    owner_username = django_filters.CharFilter(field_name='owner__username', lookup_expr='iexact')
    skill = django_filters.CharFilter(field_name='tech_stack__name', lookup_expr='iexact')
    tag = django_filters.CharFilter(method='filter_by_tag')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Project
        fields = ['project_type', 'is_featured', 'owner_username', 'skill', 'min_stars', 'max_stars', 'created_after']

    def filter_by_tag(self, queryset, name, value):
        # Filter for tag contained within the JSON tags list or icontains in fallback
        return queryset.filter(tags__icontains=value)

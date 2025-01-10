from django_filters import rest_framework as filters
from .models import Job


class JobFilter(filters.FilterSet):
    status = filters.CharFilter(lookup_expr='icontains')
    scheduled_time = filters.DateTimeFilter(field_name='scheduled_time', lookup_expr='gte')
    created_at = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Job
        fields = ['status', 'scheduled_time', 'created_at']

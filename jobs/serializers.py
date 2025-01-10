# serializers.py
from django.utils import timezone 
from rest_framework import serializers
from .models import Job, JobResult

class JobResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobResult
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'name',
            'description', 
            'created_at',
            'scheduled_time', 
            'status',
            'result',
        ]
        read_only_fields = [
            'id', 
            'created_at',
            'status',
            'result', 
        ]

    def validate_scheduled_time(self,value):
        if value <= timezone.now():
            raise serializers.ValidationError({"detail" : "we cant really schedule for past can we einestein?"})
        return value 



from django.db.models import Count
from jobs.models import Job
from rest_framework import status
from rest_framework.response import Response
from users.perms import IsVerified
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DashboardApiView(GenericViewSet):
    permission_classes = [IsVerified]
    
    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)




    @swagger_auto_schema(
        operation_description="Retrieve a summary of job statuses for the authenticated user.",
        responses={
            200: openapi.Response(
                description="Job status summary retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER),
                    example={
                        "pending": 5,
                        "in_progress": 3,
                        "completed": 2,
                        "cancelled": 0,
                    },
                ),
            ),
            401: openapi.Response(
                description="Unauthorized - User is not authenticated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                    },
                ),
            ),
            403: openapi.Response(
                description="Forbidden - User is not verified",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                    },
                ),
            ),
        },
        security=[{"Bearer": []}],
    )
    def list(self, request, *args, **kwargs):
        status_counts = self.get_queryset().values('status').annotate(count=Count('status'))

        status_summary = {item['status']: item['count'] for item in status_counts}

        all_statuses = dict(Job.STATUS_CHOICES)
        for status_key in all_statuses:
            if status_key not in status_summary:
                status_summary[status_key] = 0
        return Response(status_summary, status=status.HTTP_200_OK)

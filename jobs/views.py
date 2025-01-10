from rest_framework import viewsets
from jobs.perms import IsVerifiedAndTaskOwner
from .models import Job, JobResult
from .serializers import JobResultSerializer, JobSerializer
from .tasks import process_job
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from celery import current_app
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from .filters import JobFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi





class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsVerifiedAndTaskOwner]
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = JobFilter
    ordering_fields = ['status', 'scheduled_time', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)  # type:ignore

    def perform_create(self, serializer):
        job = serializer.save(user=self.request.user)
        task_id = process_job.apply_async(args=[job.id], eta=job.scheduled_time) #type:ignore
        job.task_id = task_id
        job.save()
    

    @swagger_auto_schema(
        operation_description="Retrieve results for a specific job.",
        responses={
            200: openapi.Response(
                description="Job results retrieved successfully",
                schema=JobResultSerializer(many=True),
            ),
            404: openapi.Response(
                description="Job not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                    },
                ),
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID of the job to retrieve results for",
                required=True,
            ),
        ],
        security=[{"Bearer": []}],
    )
    @action(
        detail=True,
    )
    def result(self,request,pk=None):
        job = self.get_object()
        results = JobResult.objects.filter( #type:ignore
            job=job 
        )
        return Response(
            JobResultSerializer(results,many=True).data
        )


    def destroy(self, request, *args, **kwargs):
        job = self.get_object()

        if job.status == 'in-progress':
            return Response(
                {'detail': "The job is already under process"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            

        if job.status == "pending":
            current_app.control.revoke(job.task_id, terminate=True)



        return super().destroy(request, *args, **kwargs)

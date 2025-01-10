from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from .models import Job, JobResult
from .views import JobViewSet
from .serializers import JobSerializer, JobResultSerializer
from .filters import JobFilter

User = get_user_model()

class JobViewSetTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            is_verified=True,
        )
        self.job = Job.objects.create(
            user=self.user,
            name='Test Job',
            description='This is a test job',
            scheduled_time='2023-12-31T23:59:59Z',
            status='pending',
        )
        self.job_result = JobResult.objects.create(
            job=self.job,
            output='Job completed successfully',
            error_message=None,
            completed_at='2023-12-31T23:59:59Z',
        )
        self.url = '/jobs/'

    def test_list_jobs(self):
        view = JobViewSet.as_view({'get': 'list'})
        request = self.factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one job for this user

    def test_create_job(self):
        view = JobViewSet.as_view({'post': 'create'})
        data = {
            'name': 'New Job',
            'description': 'This is a new job',
            'scheduled_time': '2026-01-01T00:00:00Z',
            'status': 'pending',
        }
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 2) 

    def test_retrieve_job(self):
        view = JobViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(f'{self.url}{self.job.id}/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.job.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.job.name)

    def test_update_job(self):
        view = JobViewSet.as_view({'put': 'update'})
        data = {
            'name': 'Updated Job',
            'description': 'This job has been updated',
            'scheduled_time': '2026-01-01T00:00:00Z',
            'status': 'in-progress',
        }
        request = self.factory.put(f'{self.url}{self.job.id}/', data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.job.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.name, 'Updated Job')
    


    def test_delete_job(self):
        view = JobViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'{self.url}{self.job.id}/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.job.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Job.objects.count(), 0)

    def test_delete_job_in_progress(self):
        self.job.status = 'in-progress'
        self.job.save()
        view = JobViewSet.as_view({'delete': 'destroy'})
        request = self.factory.delete(f'{self.url}{self.job.id}/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.job.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Job.objects.count(), 1)

    def test_result_action(self):
        view = JobViewSet.as_view({'get': 'result'})
        request = self.factory.get(f'{self.url}{self.job.id}/result/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.job.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One result for this job

    def test_filter_jobs_by_status(self):
        view = JobViewSet.as_view({'get': 'list'})
        Job.objects.create(
            user=self.user,
            name='Completed Job',
            description='This job is completed',
            scheduled_time='2024-01-01T00:00:00Z',
            status='completed',
        )
        request = self.factory.get(self.url, {'status': 'completed'})
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one completed job

    def test_order_jobs_by_created_at(self):
        view = JobViewSet.as_view({'get': 'list'})
        Job.objects.create(
            user=self.user,
            name='Newer Job',
            description='This is a newer job',
            scheduled_time='2024-01-01T00:00:00Z',
            status='pending',
        )
        request = self.factory.get(self.url, {'ordering': '-created_at'})
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Newer Job')  # Newer job first

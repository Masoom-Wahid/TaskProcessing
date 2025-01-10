from celery import shared_task
from django.db import transaction
import time
from django.utils import timezone
from .models import Job, JobResult

@shared_task(bind=True, max_retries=3)
def process_job(self, job_id):
    try:
        job = Job.objects.get(id=job_id)
        job.status = 'in-progress'
        job.save()

        time.sleep(10)  

        with transaction.atomic():
            job.status = 'completed'
            job.result = "Job completed successfully!"
            job.save()
            
            JobResult.objects.create(
                job=job,
                output="Completed", 
                completed_at=timezone.now()
            )

    except Job.DoesNotExist:
        return

    except Exception as e:
        with transaction.atomic():
            job.status = 'failed'
            job.save()
            JobResult.objects.create(
                job=job,
                output="failed",
                error_message=str(e),
                completed_at=timezone.now()
            )
        self.retry(exc=e, countdown=60)

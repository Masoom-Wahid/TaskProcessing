from django.db import models
from django.contrib.auth import get_user_model

class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    task_id = models.CharField(max_length=128,null=True,blank=True)
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.status})"




class JobResult(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    output = models.TextField(blank=False, null=False)
    error_message = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    

    def __str__(self) -> str:
        return f"Job -> {self.job.name}, Output->{self.output}"






# Create your models here.
from django.db import models
from users.models import User

from news_lynk import settings


class Summarised_Feedback(models.Model):
    topic = models.CharField(max_length=255)
    ai_topic = models.CharField(max_length=255, blank=True, null=True)
    ai_problem = models.TextField(blank=True, null=True)
    ai_solution = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.topic


class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('work_related', 'Work Related'),
        ('culture_related', 'Culture Related'),
    ]
    DEPARTMENT_CHOICES = [
        ('it', 'IT'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('marketing', 'Marketing'),
        ('office supplies', 'Office Supplies'),
        ('sales', 'Sales'),
        ('other', 'Other'),
    ]
    tags = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    topic = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    description = models.TextField()
    effect = models.TextField()
    suggestions = models.TextField(blank=True, null=True)
    tools = models.CharField(max_length=255, blank=True, null=True)
    affected_areas = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='feedbacks')
    subtopic = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.topic

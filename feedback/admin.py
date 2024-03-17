from django.contrib import admin
from .models import Feedback, Summarised_Feedback
# Register your models here.
admin.site.register(Feedback)
admin.site.register(Summarised_Feedback)

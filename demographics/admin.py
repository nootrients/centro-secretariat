from django.contrib import admin

from .models import ScholarshipType, Gender

# Register your models here.
admin.site.register(ScholarshipType)
admin.site.register(Gender)
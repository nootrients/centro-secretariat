from django.contrib import admin

from .models import PartneredUniversities, Courses, Applications, ApplicationStatus

# admin.site.register(PartneredUniversities)
# admin.site.register(Courses)
admin.site.register(Applications)
admin.site.register(ApplicationStatus)
from django.contrib import admin

from .models import PartneredUniversities, Courses, Applications, ApplicationStatus, TempApplications

# admin.site.register(PartneredUniversities)
# admin.site.register(Courses)
admin.site.register(Applications)
admin.site.register(ApplicationStatus)
admin.site.register(TempApplications)
from django.contrib import admin

from .models import PartneredUniversities, Courses, Applications, TempApplications, StatusUpdate, EligibilityConfig, AuditLog, TempApplicationIdCounter

# admin.site.register(PartneredUniversities)
# admin.site.register(Courses)
admin.site.register(Applications)
admin.site.register(TempApplications)
admin.site.register(AuditLog)
admin.site.register(EligibilityConfig)
admin.site.register(TempApplicationIdCounter)
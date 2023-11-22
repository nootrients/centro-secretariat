from django.contrib import admin
from django.urls import path, include

from accounts.views import MyTokenObtainPairView

from rest_framework_simplejwt.views import TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Index / Home / Root AND Scholarship Submission / Retrieval / Tracking
    path('', include('index.urls')),
    # Path for Head Scholarship Officer as a SuperUser
    path('admin/', admin.site.urls),
    
    # For API Viewing
    path('accounts/', include('accounts.urls')),
    path('applications/', include('application.urls')),
    
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('survey/', include('survey.urls')),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
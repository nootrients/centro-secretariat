from django.contrib import admin
from django.urls import path, include

from accounts.views import MyTokenObtainPairView

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Index / Home / Root AND Scholarship Submission / Retrieval / Tracking
    path('', include('index.urls')),
    # Path for Head Scholarship Officer as a SuperUser
    path('admin/', admin.site.urls),
    
    # For API Viewing
    path('accounts/', include('accounts.urls')),
    
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Application
    path('application/', include('application.urls')),
]

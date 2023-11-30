from django.urls import path

from . import views


urlpatterns = [
    path('profile/', views.UserProfileDetail.as_view(), name='user_profile'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
    
    path('users/', views.AccountList.as_view(), name='list_all_registered_accounts'),
    path('users/create/', views.CreateOfficer.as_view(), name='create-officer'),
    path('users/<str:username>/', views.CustomUserDetailView.as_view(), name='user-detail'),
]
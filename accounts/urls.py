from django.urls import path

from . import views


urlpatterns = [
    path('profile/', views.UserProfileDetail.as_view(), name='user_profile'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change_password'),
    
    path('users/staff/', views.StaffList.as_view(), name='list_all_staff_accounts'),
    path('users/staff/create/', views.CreateOfficer.as_view(), name='create-officer'),
    path('users/staff/<str:username>/', views.CustomUserDetailView.as_view(), name='staff-detail'),

    path('users/scholars/', views.ScholarList.as_view(), name='list_all_scholar_accounts'),
    path('users/scholars/<str:username>/', views.ScholarDetailView.as_view(), name='scholar-detail'),
]
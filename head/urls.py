from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("index/", views.index, name="index"),
    path("manageCriteria/", views.manageCriteria, name="manageCriteria"),
]

from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

]+static(settings.MEDIA_URL, document_route=settings.MEDIA_ROOT)
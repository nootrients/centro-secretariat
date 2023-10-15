from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import UpdateModelMixin

from rest_framework import mixins

class AllowPUTAsCreateMixin(mixins.CreateModelMixin, mixins.UpdateModelMixin):

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except Http404:
            pass
        return self.create(request, *args, **kwargs)
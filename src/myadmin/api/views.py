from django.apps import apps
from rest_framework import viewsets

from myadmin.api.serializers import GeneralSerializer


class GeneralViewSet(viewsets.ModelViewSet):

    @property
    def model(self):
        return apps.get_model(str(self.kwargs['model_name']).lower())

    def get_queryset(self):
        return self.model.objects.all()

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

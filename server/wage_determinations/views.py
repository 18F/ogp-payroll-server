from . import serializers, models

from rest_framework import viewsets

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.County.objects.all()
    serializer_class = serializers.CountySerializer

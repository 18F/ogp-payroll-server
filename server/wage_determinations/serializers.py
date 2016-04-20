from rest_framework import routers, serializers, viewsets

from . import models

class WageDeterminationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WageDetermination


class RateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Rate


class CountySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.County

class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.State

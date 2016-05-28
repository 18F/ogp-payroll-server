from rest_framework import serializers

from . import models


class WageDeterminationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WageDetermination


class RateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Rate
        exclude = ('counties', )


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.State


class CountySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.County

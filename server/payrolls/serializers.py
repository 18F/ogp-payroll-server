from django.contrib.auth.models import User
from rest_framework import serializers

from wage_determinations.serializers import CountySerializer

from . import models


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Location


class ContractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contractor


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Project


class PayrollSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Payroll


class PayrollUploadSerializer(serializers.HyperlinkedModelSerializer):
    uploader = serializers.SlugRelatedField(read_only=True, slug_field='id')

    class Meta:
        model = models.PayrollUpload
        read_only_fields = ('created', 'datafile', 'uploader')


class UserSerializer(serializers.ModelSerializer):
    payrolls = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Payroll.objects.all())
    contractors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Contractor.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'payrolls', 'contractors')

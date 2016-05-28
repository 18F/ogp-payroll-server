from django.contrib.auth.models import User
from rest_framework import serializers

from . import models


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Location


class ContractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contractor
        fields = ('url',
                  'cage',
                  'name',
                  'address',
                  'created',
                  'modified',
                  'submitter',
                  'projectcontractor_set', )


class ProjectContractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ProjectContractor


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Project


class DaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Day


class LineQuantitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.LineQuantity


class PayrollLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PayrollLine

    day_set = DaySerializer(many=True)
    linequantity_set = LineQuantitySerializer(many=True)


class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Worker


class FringeExceptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.FringeException


class WorkweekSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Workweek

    payrollline_set = PayrollLineSerializer(many=True)


class PayrollSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Payroll

    workweek_set = WorkweekSerializer(many=True)
    fringeexception_set = FringeExceptionSerializer(many=True)


class PayrollUploadSerializer(serializers.HyperlinkedModelSerializer):
    uploader = serializers.SlugRelatedField(read_only=True, slug_field='id')

    class Meta:
        model = models.PayrollUpload
        read_only_fields = ('created', 'datafile', 'uploader')


class UserSerializer(serializers.ModelSerializer):
    payrolls = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Payroll.objects.all())
    contractors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Contractor.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'payrolls', 'contractors')

from rest_framework import serializers
from django.contrib.auth.models import User

from . import models


class ContractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contractor


class PayrollSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Payroll


class UserSerializer(serializers.ModelSerializer):
    payrolls = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Payroll.objects.all())
    contractors = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Contractor.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'payrolls', 'contractors')

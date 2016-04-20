from . import serializers, models

from rest_framework import viewsets, generics
from django.contrib.auth.models import User

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = models.Payroll.objects.all()
    serializer_class = serializers.PayrollSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

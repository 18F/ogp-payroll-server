import csv

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import (exceptions, generics, parsers, permissions, status,
                            views, viewsets)
from rest_framework.response import Response

from . import models, serializers, uploaders


class LocationViewSet(viewsets.ModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        location = models.Location.make(request.data)
        location.save()
        headers = self.get_success_headers(serializer.initial_data)
        return Response(
            {"url": "/location/{}/".format(location.pk)},
            status=status.HTTP_201_CREATED,
            headers=headers)


class ContractorViewSet(viewsets.ModelViewSet):
    queryset = models.Contractor.objects.all()
    serializer_class = serializers.ContractorSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = models.Payroll.objects.all()
    serializer_class = serializers.PayrollSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class PayrollUploadViewSet(viewsets.ModelViewSet):

    queryset = models.PayrollUpload.objects.all()
    serializer_class = serializers.PayrollUploadSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, )

    def perform_create(self, serializer):
        import ipdb
        ipdb.set_trace()
        raw = self.request.data['datafile'].read()
        uploaders.AmgUploader(self.request).upload(raw)
        self.request.data['datafile'].seek(0)
        serializer.save(uploader=self.request.user,
                        datafile=self.request.data.get('datafile'))

    # curl -u catherine:ogppayroll -X POST "127.0.0.1:8000/payrollupload/?filename=payroll.csv" -d '{"name" = "AGP payroll","source"="/Users/catherine/dock/ogp/dump/amg_payroll.csv"}' -H "Content-Type: application/json"

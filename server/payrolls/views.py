import csv

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import (exceptions, generics, parsers, permissions, status,
                            views, viewsets)
from rest_framework.decorators import detail_route
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
    filter_fields = ('cage', 'name', 'submitter', )


class ProjectContractorViewSet(viewsets.ModelViewSet):
    queryset = models.ProjectContractor.objects.all()
    serializer_class = serializers.ProjectContractorSerializer


class FringeExceptionViewSet(viewsets.ModelViewSet):
    queryset = models.FringeException.objects.all()
    serializer_class = serializers.FringeExceptionSerializer


class DayViewSet(viewsets.ModelViewSet):
    queryset = models.Day.objects.all()
    serializer_class = serializers.DaySerializer


class LineQuantityViewSet(viewsets.ModelViewSet):
    queryset = models.LineQuantity.objects.all()
    serializer_class = serializers.LineQuantitySerializer


class PayrollLineViewSet(viewsets.ModelViewSet):
    queryset = models.PayrollLine.objects.all()
    serializer_class = serializers.PayrollLineSerializer


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = models.Worker.objects.all()
    serializer_class = serializers.WorkerSerializer


class WorkweekViewSet(viewsets.ModelViewSet):
    queryset = models.Workweek.objects.all()
    serializer_class = serializers.WorkweekSerializer


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = models.Payroll.objects.all()
    serializer_class = serializers.PayrollSerializer

    def get_queryset(self):
        queryset = models.Payroll.objects
        if 'cage' in self.request.query_params:
            queryset = queryset.filter(
                contractor__cage=self.request.query_params['cage'])
        return queryset.all()

    @detail_route(methods=['post', ])
    def clone(self, request, *args, **kwargs):
        original = self.get_object()
        new = original.clone(payroll_number=request.data['payroll_number'],
                             period_end=request.data['period_end'])
        return Response({'url': '/payroll/{}/'.format(new.id)})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class PayrollUploadViewSet(viewsets.ModelViewSet):

    queryset = models.PayrollUpload.objects.all()
    serializer_class = serializers.PayrollUploadSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,
                      parsers.JSONParser, parsers.FileUploadParser)

    # TODO: accept upload that does not contain the payroll,
    # is just an attachment

    def perform_create(self, serializer):
        raw = self.request.data['datafile'].read()
        payroll = uploaders.upload(self.request, raw)
        self.request.data['datafile'].seek(0)
        serializer.save(uploader=self.request.user,
                        datafile=self.request.data.get('datafile'),
                        payroll=payroll)

    """sample API calls for a complete upload:

    curl -u catherine:ogppayroll -X POST "http://localhost:8000/location/" -d '{"street": "1800 F St NW", "zip_code": "20006", "state": "DC", "city": "Washington", "county": "1"}' -H "Content-Type: application/json"

    curl -u catherine:ogppayroll -X POST "http://localhost:8000/project/" -d '{"name": "Awesome Digital America", "project_number": "AMG123", "location": "/location/16/"}' -H "Content-Type: application/json"

    curl -X POST -H "Content-Type:multipart/form-data" -u catherine:ogppayroll -F "project_id=1" -F "datafile=@/Users/catherine/dock/ogp/dump/amg_payroll.csv;type=application/csv" https://localhost:8000/payrollupload/
    """

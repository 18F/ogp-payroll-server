from . import serializers, models

from rest_framework import viewsets, views
from rest_framework.response import Response

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.County.objects.all()
    serializer_class = serializers.CountySerializer

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateSerializer

class WageDeterminationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.WageDetermination.objects.all()
    serializer_class = serializers.WageDeterminationSerializer

class RateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Rate.objects.all()
    serializer_class = serializers.RateSerializer

class RateSearchList(views.APIView):

    def get_queryset(self, *args, **kwargs):
        rates = models.Rate.objects.all()[:4]
        return rates

    def get(self, request, format=None, q=''):
        qry = 'SELECT * FROM wage_determinations_rate WHERE fts_index @@ to_tsquery(%s)'
        rates = models.Rate.objects.raw(qry, (' & '.join(q.split()),))
        serializer = serializers.RateSerializer(rates, many=True, context={'request': request})
        return Response(serializer.data)

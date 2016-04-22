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

    def _parse_terms(self, terms):
        (county, state, q) = ('', '', '')
        for piece in terms.split('&'):
            if '=' in piece:
                param = piece.split('=')[0].strip().lower()
                if param == 'st':
                    state = piece.split('=')[1].strip().lower()
                elif param == 'co':
                    county = piece.split('=')[1].strip().lower()
            else:
                q = piece.strip()
        return {'q': q, 'st': state.title(), 'co': county.title()}

    _qry = """
        SELECT r.*
        FROM   wage_determinations_rate r
        JOIN   wage_determinations_rate_counties rc
          ON rc.rate_id = r.id
        JOIN   wage_determinations_county c
          ON rc.county_id = c.id
        JOIN   wage_determinations_state s
          ON c.us_state_id = s.id
        WHERE  fts_index @@ to_tsquery(%(q)s)
        AND    s.name = %(st)s
        AND    c.name = %(co)s
        """

    def get(self, request, format=None, terms=''):
        terms = self._parse_terms(terms)
        # TODO: handle missing state, county
        rates = models.Rate.objects.raw(self._qry, terms)
        serializer = serializers.RateSerializer(rates, many=True, context={'request': request})
        return Response(serializer.data)

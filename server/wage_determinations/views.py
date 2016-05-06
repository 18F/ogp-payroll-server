from . import serializers, models

from rest_framework import viewsets, views, status
from rest_framework.response import Response

class CountyViewSet(viewsets.ModelViewSet):
    queryset = models.County.objects.all()
    serializer_class = serializers.CountySerializer


class StateViewSet(viewsets.ModelViewSet):
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
                    state = piece.split('=')[1].strip()
                elif param == 'co':
                    county = piece.split('=')[1].strip()
            else:
                q = piece.strip()
        return {'q': q, 'st': state.upper(), 'co': county.upper()}

    _qry = """
        SELECT r.*
        FROM   wage_determinations_rate r
        JOIN   wage_determinations_rate_counties rc
          ON rc.rate_id = r.id
        JOIN   wage_determinations_county c
          ON rc.county_id = c.id
        JOIN   wage_determinations_state s
          ON c.us_state_id = s.id
        {} LIMIT {}"""

    def qry(self):
        # this is SOOOOO sql-injectable
        filters = []
        if 'q' in self.request.query_params:
            filters.append("fts_index @@ to_tsquery(%(q)s)")
            # TODO: sort by hit quality
        if 'st' in self.request.query_params:
            filters.append("(s.name = UPPER(%(st)s) OR s.abbrev = UPPER(%(st)s))")
        if 'co' in self.request.query_params:
            filters.append("c.name = UPPER(%(co)s)")
        if filters:
            filters = " WHERE " + " AND ".join(filters)
        else:
            filters = ""
        return self._qry.format(filters, 100)

    def get(self, request, format=None):
        qry = self.qry()
        print(qry)
        q_terms = {p: v for (p, v) in request.query_params.items()} 
        print(q_terms)
        rates = models.Rate.objects.raw(self.qry(), q_terms)
        serializer = serializers.RateSerializer(rates, many=True, context={'request': request})
        return Response(serializer.data)

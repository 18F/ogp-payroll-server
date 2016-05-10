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

    _qry = """
    SELECT {rank_term} AS rank, * FROM (
        SELECT *
        FROM   {textsearch} textsearch,
               wage_determinations_rate r
        JOIN   wage_determinations_rate_counties rc
          ON rc.rate_id = r.id
        JOIN   wage_determinations_county c
          ON rc.county_id = c.id
        JOIN   wage_determinations_state s
          ON c.us_state_id = s.id
        {filters}
        AND (s.name = UPPER('oh') OR s.abbrev = UPPER('oh'))
        AND c.name = UPPER('union')
    ) subq
    ORDER BY rank DESC, occupation, rate_name, subrate_name
    LIMIT {limit}
    """

    def qry(self):
        filters = []
        params = dict(self.request.query_params)
        if 'q' in self.request.query_params:
            rank_term = 'ts_rank_cd(fts_index, textsearch)'
            textsearch = "TO_TSQUERY(%(q)s)"
            filters.append("fts_index @@ to_tsquery(%(q)s)")
        else:
            rank_term = 'NULL'
            textsearch = "(SELECT 'no text search')"
        if 'st' in self.request.query_params:
            filters.append("(s.name = UPPER(%(st)s) OR s.abbrev = UPPER(%(st)s))")
        if 'co' in self.request.query_params:
            filters.append("c.name = UPPER(%(co)s)")
        if 'cat' in self.request.query_params:
            filters.append("r.construction_type = UPPER(%(cat)s)")
        if filters:
            filters = " WHERE " + " AND ".join(filters)
        else:
            filters = ""
        return self._qry.format(rank_term=rank_term, textsearch=textsearch, filters=filters, limit=100)

    def get(self, request, format=None):
        qry = self.qry()
        print(qry)
        q_terms = {p: v for (p, v) in request.query_params.items()}
        print(q_terms)
        rates = models.Rate.objects.raw(self.qry(), request.query_params)
        serializer = serializers.RateSerializer(rates, many=True, context={'request': request})
        return Response(serializer.data)

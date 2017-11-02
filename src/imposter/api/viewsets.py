from rest_framework import viewsets, permissions

from imposter.api.serializers import BureauSerializer, SpecSerializer, PosterSerializer, PosterUpdateSerializer
from imposter.models import Bureau, PosterSpec, Poster, PosterImage


class BureauViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bureau.objects.enabled()
    serializer_class = BureauSerializer


class PosterSpecViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PosterSpec.objects.enabled()
    serializer_class = SpecSerializer


class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.select_related('bureau', 'spec')

    def filter_queryset(self, queryset):

        qs = super().filter_queryset(self.get_queryset())

        since = self.request.query_params.get('since')
        if since:
            qs = qs.filter(created__gte=since)

        until = self.request.query_params.get('until')
        if until:
            qs = qs.filter(created__lte=until)

        bureau = self.request.query_params.get('bureau')
        if bureau:
            qs = qs.filter(bureau_id=bureau)

        template = self.request.query_params.get('template')
        if template:
            qs = qs.filter(spec_id=template)

        limit = self.request.query_params.get('limit')
        if limit:
            offset = self.request.query_params.get('offset', 0)
            qs = qs[offset:offset+limit]

        return qs

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return PosterSerializer

        return PosterUpdateSerializer

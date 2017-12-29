from django.utils.translation import ugettext as _

from rest_framework import permissions, response, status, viewsets

from imposter.api.permissions import IsObjectEditable
from imposter.api.serializers import BureauSerializer, SpecSerializer, PosterSerializer, PosterCreateUpdateSerializer
from imposter.models.bureau import Bureau
from imposter.models.poster import Poster
from imposter.models.posterspec import PosterSpec


class BureauViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bureau.objects.enabled()
    serializer_class = BureauSerializer


class PosterSpecViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PosterSpec.objects.enabled()
    serializer_class = SpecSerializer


class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.select_related('bureau', 'spec')
    permission_classes = IsObjectEditable,

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # Avoiding HTTP_204_NO_CONTENT
        return response.Response(dict(detail=_('Successfully deleted.')), status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return PosterSerializer

        return PosterCreateUpdateSerializer

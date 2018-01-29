from dateutil.parser import parse

from django.utils.translation import ugettext as _

from rest_framework import permissions, response, status, viewsets, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from imposter.api.permissions import IsObjectEditable
from imposter.api.serializers import BureauSerializer, SpecSerializer, PosterSerializer, PosterCreateUpdateSerializer
from imposter.models.bureau import Bureau
from imposter.models.poster import Poster
from imposter.models.posterspec import PosterSpec


class APIRootView(generics.RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        return Response({
            'bureau': reverse('bureau-list'),
            'spec': reverse('posterspec-list'),
            'poster': reverse('poster-list'),
        })


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
        filter_errors = []

        since = self.request.query_params.get('since')
        if since:
            try:
                qs = qs.filter(created__gte=parse(since))
            except ValueError:
                filter_errors.append(_("Invalid date format of 'since': {val}").format(val=since))

        until = self.request.query_params.get('until')
        if until:
            try:
                qs = qs.filter(created__lte=parse(until))
            except ValueError:
                filter_errors.append(_("Invalid date format of 'until': {val}").format(val=until))

        bureau = self.request.query_params.get('bureau')
        if bureau:
            try:
                qs = qs.filter(bureau_id=int(bureau))
            except ValueError:
                filter_errors.append(_("Invalid 'bureau' ID: {val}").format(val=bureau))

        spec = self.request.query_params.get('spec')
        if spec:
            try:
                qs = qs.filter(spec_id=int(spec))
            except ValueError:
                filter_errors.append(_("Invalid 'spec' ID: {val}").format(val=spec))

        if filter_errors:
            raise ValidationError(dict(filters=filter_errors))

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

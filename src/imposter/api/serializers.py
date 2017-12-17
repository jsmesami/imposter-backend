from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from imposter.models.bureau import Bureau
from imposter.models.poster import Poster
from imposter.models.posterspec import PosterSpec


class BureauSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bureau
        fields = 'id name abbrev number address'.split()


class SpecListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterSpec
        fields = 'id name color'.split()


class SpecSerializer(serializers.ModelSerializer):

    thumb = serializers.SerializerMethodField()

    def get_thumb(self, instance):
        return instance.thumb.url

    class Meta:
        model = PosterSpec
        fields = 'id name color thumb editable_fields'.split()


class PosterSerializer(serializers.ModelSerializer):

    bureau = BureauSerializer(read_only=True)
    spec = SpecListSerializer(read_only=True)
    thumb = serializers.SerializerMethodField()
    print = serializers.SerializerMethodField()
    fields = serializers.JSONField(source='saved_fields')

    def get_thumb(self, instance):
        return instance.thumb.url

    def get_print(self, instance):
        return instance.print.url

    class Meta:
        model = Poster
        fields = 'id editable title thumb print bureau spec fields'.split()


class PosterCreateUpdateSerializer(serializers.ModelSerializer):

    bureau = serializers.PrimaryKeyRelatedField(queryset=Bureau.objects.enabled())
    spec = serializers.PrimaryKeyRelatedField(queryset=PosterSpec.objects.enabled())
    fields = serializers.JSONField(source='saved_fields')

    @staticmethod
    def specs_validator(field_type, field_name, field_values, saved_field_values):
        assert field_type in PosterSpec.FIELD_SPECS.keys()

        editable_values = PosterSpec.FIELD_SPECS[field_type]['editable']
        disallowed_specs = set(field_values.keys()) - editable_values
        if disallowed_specs:
            raise ValidationError("Specs not allowed for {type} field '{name}': {specs}".format(
                type=field_type,
                name=field_name,
                specs=', '.join(disallowed_specs),
            ))

        mandatory_specs = PosterSpec.FIELD_SPECS[field_type]['mandatory']
        missing_required_specs = mandatory_specs - set(saved_field_values.keys()) - set(field_values.keys())
        if missing_required_specs:
            raise ValidationError("Missing required specs for {type} field '{name}': {specs}".format(
                type=field_type,
                name=field_name,
                specs=', '.join(missing_required_specs),
            ))

    def validate_fields(self, fields):
        if self.instance:
            saved_fields = self.instance.saved_fields
            spec_object = self.instance.spec
        else:
            saved_fields = {}
            spec_id = self.initial_data.get('spec')
            try:
                spec_object = PosterSpec.objects.get(pk=spec_id)
            except PosterSpec.DoesNotExist:
                raise ValidationError('Cannot retreive poster specification of ID {}.'.format(spec_id))

        # Do not allow passing fields that are not in spec
        disallowed_fields = (
            set(fields.keys()) -
            set(spec_object.editable_fields.keys())
        )
        if disallowed_fields:
            raise ValidationError('Fields not allowed: ' + ', '.join(disallowed_fields))

        # Check if all required fields are present
        missing_required_fields = (
            set(spec_object.mandatory_fields.keys()) -
            set(saved_fields.keys()) -
            set(fields.keys())
        )
        if missing_required_fields:
            raise ValidationError('Missing required fields: ' + ', '.join(missing_required_fields))

        # Recursively check if fields have valid specs
        def validate_specs(fields, parent_type=None):
            for field_name, field_values in fields.items():
                field_type = spec_object.fields.get(field_name, {}).get('type')
                children = field_values.get('fields')
                if children:
                    validate_specs(children, field_type)
                else:
                    saved_field_values = saved_fields.get(field_name, {})
                    self.specs_validator(parent_type or field_type, field_name, field_values, saved_field_values)

        validate_specs(fields)

        return fields

    class Meta:
        model = Poster
        fields = 'id bureau spec fields'.split()

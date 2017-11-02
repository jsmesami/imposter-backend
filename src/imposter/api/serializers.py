from copy import deepcopy

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from imposter.models import Bureau, PosterSpec, Poster, PosterImage
from utils.functional import deepmerge


class BureauSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bureau
        fields = 'id name abbrev number address'.split()


class SpecListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterSpec
        fields = 'id name color'.split()


class SpecSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosterSpec
        fields = 'id name color thumb editable_fields'.split()


class PosterSerializer(serializers.ModelSerializer):

    bureau = BureauSerializer(read_only=True)
    spec = SpecListSerializer(read_only=True)

    class Meta:
        model = Poster
        fields = 'id editable title thumb print bureau spec saved_fields'.split()


class PosterUpdateSerializer(serializers.ModelSerializer):

    bureau = serializers.PrimaryKeyRelatedField(queryset=Bureau.objects.enabled())
    spec = serializers.PrimaryKeyRelatedField(queryset=PosterSpec.objects.enabled())
    fields = serializers.JSONField(source='saved_fields')

    @staticmethod
    def specs_validator(field_type, field_name, field_specs):
        assert field_type in PosterSpec.FIELD_SPECS.keys()

        editable_specs = PosterSpec.FIELD_SPECS[field_type]['editable']
        disallowed_specs = set(field_specs.keys()) - editable_specs
        if disallowed_specs:
            raise ValidationError("Specs not allowed for {type} field '{name}': {specs}".format(
                type=field_type,
                name=field_name,
                specs=', '.join(disallowed_specs),
            ))

        mandatory_specs = PosterSpec.FIELD_SPECS[field_type]['mandatory']
        missing_required_specs = mandatory_specs - set(field_specs.keys())
        if missing_required_specs:
            raise ValidationError("Missing required specs for {type} field '{name}': {specs}".format(
                type=field_type,
                name=field_name,
                specs=', '.join(missing_required_specs),
            ))

    def validate_fields(self, fields):
        try:
            spec_object = PosterSpec.objects.get(pk=self.initial_data.get('spec'))
        except PosterSpec.DoesNotExist:
            raise ValidationError('Cannot retreive poster specification')

        # Do not allow passing fields that are not in spec
        disallowed_fields = set(fields.keys()) - set(spec_object.editable_fields.keys())
        if disallowed_fields:
            raise ValidationError('Fields not allowed: ' + ', '.join(disallowed_fields))

        # Check if all required fields are present
        missing_required_fields = set(spec_object.mandatory_fields.keys()) - set(fields.keys())
        if missing_required_fields:
            raise ValidationError('Missing required fields: ' + ', '.join(missing_required_fields))

        # Recursively check if fields have valid specs
        def validate_specs(fields, parent_type=None):
            for field_name, field_specs in fields.items():
                field_type = spec_object.fields.get(field_name, {}).get('type')
                children = field_specs.get('fields')
                if children:
                    validate_specs(children, field_type)
                else:
                    field_type = parent_type or field_type
                    self.specs_validator(field_type, field_name, field_specs)

        validate_specs(fields)

        return fields

    def create(self, validated_data):
        stripped_data = deepcopy(validated_data)
        stripped_data['saved_fields'] = {}
        instance = super().create(stripped_data)
        return self.update(instance, validated_data)

    def update(self, instance, validated_data):
        instance.images.all().delete()

        populated_fields = deepmerge(
            validated_data.get('saved_fields', instance.saved_fields),
            instance.spec.editable_fields)

        transformed_fields = PosterImage.save_images_from_fields(populated_fields, poster=instance)

        instance.bureau = validated_data.get('bureau', instance.bureau)
        instance.spec = validated_data.get('spec', instance.spec)
        instance.saved_fields = transformed_fields

        instance.save()
        return instance

    class Meta:
        model = Poster
        fields = 'bureau spec fields'.split()

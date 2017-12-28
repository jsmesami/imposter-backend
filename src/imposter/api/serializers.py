from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from imposter.models.bureau import Bureau
from imposter.models.image import ImageError
from imposter.models.poster import Poster
from imposter.models.posterspec import PosterSpec
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


def handles_exceptions(*exceptions, msg):
    def wrapper(cls):

        class FieldsError(ValidationError):
            def __init__(self, detail):
                super().__init__(dict(fields=[msg.format(detail=detail)]))

        class Handler(cls):

            def create(self, validated_data):
                try:
                    return super().create(validated_data)
                except exceptions as e:
                    raise FieldsError(e)

            def update(self, instance, validated_data):
                try:
                    return super().update(instance, validated_data)
                except exceptions as e:
                    raise FieldsError(e)

        return Handler

    return wrapper


@handles_exceptions(ImageError, msg='Incorrect image format. {detail}')
class PosterCreateUpdateSerializer(serializers.ModelSerializer):

    bureau = serializers.PrimaryKeyRelatedField(queryset=Bureau.objects.enabled())
    spec = serializers.PrimaryKeyRelatedField(queryset=PosterSpec.objects.enabled())
    fields = serializers.JSONField(source='saved_fields')

    def update(self, instance, validated_data):
        if 'spec' in validated_data:
            raise serializers.ValidationError({
                'spec': ["Poster specification can't be changed."],
            })

        return super().update(instance, validated_data)

    def validate_fields(self, new_fields):
        if self.instance:
            merged_fields = deepmerge(new_fields, self.instance.saved_fields)
            spec_object = self.instance.spec
        else:
            merged_fields = new_fields
            spec_object = PosterSpec.objects.get(pk=self.initial_data.get('spec'))

        # Do not allow fields that are not in spec
        disallowed_fields = sorted(
            set(merged_fields.keys()) -
            set(spec_object.editable_fields.keys())
        )
        if disallowed_fields:
            raise ValidationError('Fields not allowed: ' + ', '.join(disallowed_fields))

        # Check if all required fields are present
        missing_required_fields = sorted(
            set(spec_object.mandatory_fields.keys()) -
            set(merged_fields.keys())
        )
        if missing_required_fields:
            raise ValidationError('Missing required fields: ' + ', '.join(missing_required_fields))

        # Recursively check if new fields have valid parameters
        def validate_params(fields, parent_type=None):
            for field_name, field_params in fields.items():
                field_type = spec_object.fields.get(field_name, {}).get('type')
                children = field_params.get('fields')
                if children:
                    validate_params(children, field_type)
                else:
                    self.field_params_validator(parent_type or field_type, field_name, field_params)

        validate_params(new_fields)

        return merged_fields

    @staticmethod
    def field_params_validator(field_type, field_name, field_params):
        assert field_type in PosterSpec.FIELD_PARAMS.keys()

        editable_params = PosterSpec.FIELD_PARAMS[field_type]['editable']
        disallowed_params = sorted(set(field_params.keys()) - editable_params)
        if disallowed_params:
            raise ValidationError("Parameters not allowed for {type} field '{name}': {params}".format(
                type=field_type,
                name=field_name,
                params=', '.join(disallowed_params),
            ))

        mandatory_params = PosterSpec.FIELD_PARAMS[field_type]['mandatory']
        missing_required_params = sorted(mandatory_params - set(field_params.keys()))
        if missing_required_params:
            raise ValidationError("Missing required parameters for {type} field '{name}': {params}".format(
                type=field_type,
                name=field_name,
                params=', '.join(sorted(missing_required_params)),
            ))

    class Meta:
        model = Poster
        fields = 'id bureau spec fields'.split()

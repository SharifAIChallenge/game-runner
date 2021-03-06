from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser

from game.models import Operation, OperationParameter
from run.models import Run
from run.models import ParameterValue
from storage.models import File
from storage.serializers import FileSerializer


# class FilePathSerializer(serializers.ModelSerializer):
#     file = FileSerializer(many=False)
#
#     # definition = FileDefinitionSerializer()
#
#     class Meta:
#         model = FilePath
#         fields = ('file',
#                   # 'definition',
#                   )

class ParameterValueSetSerializerField(serializers.Field):
    def to_representation(self, value):
        result = {}
        for parameter_value in value:
            # todo serialize file definition
            result[parameter_value.parameter.name] = parameter_value._value
        return result

    def to_internal_value(self, data):
        internal_value = []
        if not isinstance(data, dict):
            raise serializers.ValidationError('parameters data must be a dictionary.')
        for parameter in data:
            internal_value.append((OperationParameter.objects.get(name=parameter), data[parameter]))
        return internal_value


class OperationSerializerFiled(serializers.Field):
    def to_internal_value(self, data):
        return Operation.objects.get(name=data)

    def to_representation(self, value):
        return value.name


class RunReportSerializer(serializers.ModelSerializer):
    parameters = ParameterValueSetSerializerField(read_only=True)
    operation = OperationSerializerFiled()

    class Meta:
        model = Run
        fields = (
            'id', 'operation', 'status', 'end_time', 'log', 'parameters')
        read_only_fields = fields

    def to_representation(self, instance):
        data = super(RunReportSerializer, self).to_representation(instance)
        data['parameters'] = ParameterValueSetSerializerField().to_representation(
            instance.parameter_value_set.all().filter(parameter__is_input=False))
        return data


class RunCreateSerializer(serializers.Serializer):
    parameters = ParameterValueSetSerializerField()
    operation = OperationSerializerFiled()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def validate(self, attrs):
        given_names = [a.name for a, b in attrs['parameters']]
        for parameter in attrs['operation'].parameters.filter(is_input=True, required=True):
            if parameter.name not in given_names:
                raise ValidationError("Parameter {} is required".format(parameter.name), code='required')
        return attrs

    def create(self, validated_data):
        run = Run(operation=validated_data['operation'], owner=validated_data['owner'])
        run.save()
        for parameter_value_data in validated_data['parameters']:
            ParameterValue.objects.create(
                parameter=parameter_value_data[0],
                _value=parameter_value_data[1],
                run=run
            )
        run.parameter_set = validated_data['parameters']
        run.save()
        return run

from rest_framework import serializers


class ProgramSearchResultSerializer(serializers.Serializer):
    program_id = serializers.CharField()
    title = serializers.CharField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    category = serializers.CharField(allow_null=True, required=False)
    language = serializers.CharField(allow_null=True, required=False)
    media_type = serializers.CharField(allow_null=True, required=False)
    media_url = serializers.CharField(allow_null=True, required=False)
    thumbnail_url = serializers.CharField(allow_null=True, required=False)
    duration_seconds = serializers.IntegerField(allow_null=True, required=False)
    publish_date = serializers.DateField(allow_null=True, required=False)
    score = serializers.FloatField()

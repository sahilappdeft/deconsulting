from rest_framework import serializers

# Dynamic serializer to accept file categories
class FileUploadSerializer(serializers.Serializer):
    complex_disease = serializers.ListField(child=serializers.FileField(), required=False)
    monogenic_disease = serializers.ListField(child=serializers.FileField(), required=False)
    pharma_disease = serializers.ListField(child=serializers.FileField(), required=False)
    wellness_disease = serializers.ListField(child=serializers.FileField(), required=False)
    traits_report = serializers.ListField(child=serializers.FileField(), required=False)
    ancestry_report = serializers.ListField(child=serializers.FileField(), required=False)


from rest_framework import serializers
from .models import REQUEST_TYPE_TO_CATEGORY, AreaChoices, StatusChoices, SupportRequest


class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = [
            "id",
            "request_type",
            "category",
            "latitude",
            "longitude",
            "area",
            "note",
            "estimated_price",
            "currency",
            "language",
            "contact_method",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "category", "currency", "status", "created_at", "updated_at"]

    def validate_area(self, value):
        allowed = {choice[0] for choice in AreaChoices.choices}
        if value not in allowed:
            raise serializers.ValidationError("Unsupported area.")
        return value

    def validate_request_type(self, value):
        if value not in REQUEST_TYPE_TO_CATEGORY:
            raise serializers.ValidationError("Unsupported request_type.")
        return value

    def validate_estimated_price(self, value):
        if value < 0:
            raise serializers.ValidationError("estimated_price must be 0 or greater.")
        return value

    def create(self, validated_data):
        validated_data["category"] = REQUEST_TYPE_TO_CATEGORY[validated_data["request_type"]]
        return super().create(validated_data)


class SupportRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ["status"]

    def validate_status(self, value):
        allowed = {choice[0] for choice in StatusChoices.choices}
        if value not in allowed:
            raise serializers.ValidationError("Unsupported status.")
        return value

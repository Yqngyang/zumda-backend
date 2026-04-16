import logging
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
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
            "google_maps_url",
            "area",
            "note",
            "estimated_price",
            "currency",
            "language",
            "contact_method",
            "people",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "category",
            "currency",
            "status",
            "created_at",
            "updated_at",
        ]

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

    def validate_people(self, value):
        if value < 1:
            raise serializers.ValidationError("people must be 1 or greater.")
        return value

    def create(self, validated_data):
        instance = super().create(validated_data)

        subject = f"[Zumda] 新しいオーダー: {instance.request_type}"
        message = f"""
新しいオーダーが入りました。

ID: {instance.id}
request_type: {instance.request_type}
category: {instance.category}
area: {instance.area}
latitude: {instance.latitude}
longitude: {instance.longitude}
google_maps_url: {instance.google_maps_url}
estimated_price: {instance.estimated_price}
currency: {instance.currency}
language: {instance.language}
contact_method: {instance.contact_method}
people: {instance.people}
status: {instance.status}
note: {instance.note}
created_at: {instance.created_at}
""".strip()

        print("=== MAIL DEBUG START ===")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print(f"NOTIFICATION_EMAILS: {settings.NOTIFICATION_EMAILS}")
        print(f"EMAIL_HOST_USER exists: {bool(settings.EMAIL_HOST_USER)}")
        print(f"EMAIL_HOST_PASSWORD exists: {bool(settings.EMAIL_HOST_PASSWORD)}")

        if not settings.NOTIFICATION_EMAILS:
            print("mail skipped: NOTIFICATION_EMAILS is empty")
            print("=== MAIL DEBUG END ===")
            return instance

        try:
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.NOTIFICATION_EMAILS,
                fail_silently=False,
            )
            print(f"send_mail result: {result}")
        except Exception as e:
            print(f"mail send error: {repr(e)}")

        print("=== MAIL DEBUG END ===")

        return instance


class SupportRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ["status"]

    def validate_status(self, value):
        allowed = {choice[0] for choice in StatusChoices.choices}
        if value not in allowed:
            raise serializers.ValidationError("Unsupported status.")
        return value
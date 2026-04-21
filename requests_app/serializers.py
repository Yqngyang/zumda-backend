from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localtime
from rest_framework import serializers

from .models import (
    REQUEST_TYPE_TO_CATEGORY,
    AreaChoices,
    ChatMessageTypeChoices,
    RequestTypeChoices,
    StatusChoices,
    SupportRequest,
    SupportRequestChatMessage,
    SupportRequestChatRoom,
)


class SupportRequestSerializer(serializers.ModelSerializer):
    chat_token = serializers.UUIDField(source="chat_room.customer_token", read_only=True)

    class Meta:
        model = SupportRequest
        fields = [
            "id",
            "request_type",
            "category",
            "customer_name",
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
            "chat_token",
        ]
        read_only_fields = [
            "id",
            "category",
            "currency",
            "status",
            "created_at",
            "updated_at",
            "chat_token",
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

    def validate_customer_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("customer_name is required.")
        return value.strip()

    def validate(self, attrs):
        request_type = attrs.get("request_type")
        now = localtime()
        hour = now.hour

        if request_type == RequestTypeChoices.LUGGAGE_HELP:
            if hour < 0 or hour >= 24:
                raise serializers.ValidationError(
                    {"request_type": "Luggage transfer is available from 09:00 to 21:00."}
                )

        if request_type == RequestTypeChoices.SHOW_ME_AROUND:
            if hour < 0 or hour >= 24:
                raise serializers.ValidationError(
                    {"request_type": "Walk & talk in Tokyo is available from 09:00 to 19:00."}
                )

        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)

        chat_room = SupportRequestChatRoom.objects.create(support_request=instance)

        SupportRequestChatMessage.objects.create(
            chat_room=chat_room,
            sender="system",
            message_type=ChatMessageTypeChoices.SYSTEM,
            message="Your request has been confirmed. You can chat here.",
        )

        operator_chat_url = (
            f"https://zumda.app/?request_id={instance.id}"
            f"&token={chat_room.operator_token}"
        )

        subject = f"[Zumda] 新しいオーダー: {instance.request_type}"
        message = f"""
新しいオーダーが入りました。

ID: {instance.id}
customer_name: {instance.customer_name}
request_type: {instance.request_type}
category: {instance.category}
area: {instance.area}
latitude: {instance.latitude}
longitude: {instance.longitude}
google_maps_url: {instance.google_maps_url}
estimated_price: {instance.estimated_price}
language: {instance.language}
people: {instance.people}
note: {instance.note}
created_at: {instance.created_at}

operator_chat_url:
{operator_chat_url}
""".strip()

        try:
            recipient_list = getattr(settings, "NOTIFICATION_EMAILS", [])
            if isinstance(recipient_list, str):
                recipient_list = [email.strip() for email in recipient_list.split(",") if email.strip()]

            if recipient_list:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
        except Exception as e:
            print(f"mail send error: {e}")

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


class SupportRequestChatMessageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SupportRequestChatMessage
        fields = [
            "id",
            "sender",
            "message_type",
            "message",
            "latitude",
            "longitude",
            "google_maps_url",
            "image",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None


class SupportRequestChatMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestChatMessage
        fields = [
            "message_type",
            "message",
            "latitude",
            "longitude",
            "google_maps_url",
            "image",
        ]

    def validate(self, attrs):
        message_type = attrs.get("message_type")
        message = (attrs.get("message") or "").strip()

        if message_type == ChatMessageTypeChoices.TEXT:
            if not message:
                raise serializers.ValidationError({"message": "message is required."})

        if message_type == ChatMessageTypeChoices.LOCATION:
            if attrs.get("latitude") is None or attrs.get("longitude") is None:
                raise serializers.ValidationError(
                    {"latitude": "latitude and longitude are required for location messages."}
                )
            if not attrs.get("google_maps_url"):
                raise serializers.ValidationError(
                    {"google_maps_url": "google_maps_url is required for location messages."}
                )

        if message_type == ChatMessageTypeChoices.PHOTO:
            if not attrs.get("image"):
                raise serializers.ValidationError({"image": "image is required for photo messages."})

        return attrs


class SupportRequestChatRoomSerializer(serializers.ModelSerializer):
    messages = SupportRequestChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportRequestChatRoom
        fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = fields
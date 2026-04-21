from decimal import Decimal
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class AreaChoices(models.TextChoices):
    UENO = "ueno", "Ueno"
    AKIHABARA = "akihabara", "Akihabara"
    YUSHIMA = "yushima", "Yushima"
    ASAKUSA = "asakusa", "Asakusa"


class CategoryChoices(models.TextChoices):
    SERVICE = "service", "Service"
    EXPERIENCE = "experience", "Experience"


class RequestTypeChoices(models.TextChoices):
    LUGGAGE_HELP = "luggage_help", "Luggage transfer"
    SHOW_ME_AROUND = "show_me_around", "Walk & talk in Tokyo"


class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    ASSIGNED = "assigned", "Assigned"
    ON_THE_WAY = "on_the_way", "On the way"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class ChatRoomStatusChoices(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class ChatSenderChoices(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    OPERATOR = "operator", "Operator"
    SYSTEM = "system", "System"


class ChatMessageTypeChoices(models.TextChoices):
    TEXT = "text", "Text"
    LOCATION = "location", "Location"
    PHOTO = "photo", "Photo"
    SYSTEM = "system", "System"


REQUEST_TYPE_TO_CATEGORY = {
    RequestTypeChoices.LUGGAGE_HELP: CategoryChoices.SERVICE,
    RequestTypeChoices.SHOW_ME_AROUND: CategoryChoices.EXPERIENCE,
}


class SupportRequest(models.Model):
    request_type = models.CharField(max_length=32, choices=RequestTypeChoices.choices)
    category = models.CharField(max_length=32, choices=CategoryChoices.choices, editable=False)

    customer_name = models.CharField(max_length=100)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    google_maps_url = models.URLField(blank=True)

    area = models.CharField(max_length=32, choices=AreaChoices.choices)
    note = models.TextField(blank=True)

    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="JPY")
    language = models.CharField(max_length=16, default="en")
    contact_method = models.CharField(max_length=64, blank=True)

    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    people = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.request_type not in REQUEST_TYPE_TO_CATEGORY:
            raise ValidationError({"request_type": "Unsupported request_type."})

        if self.estimated_price is not None and self.estimated_price < 0:
            raise ValidationError({"estimated_price": "estimated_price must be 0 or greater."})

        if self.people < 1:
            raise ValidationError({"people": "people must be 1 or greater."})

        if not self.customer_name or not self.customer_name.strip():
            raise ValidationError({"customer_name": "customer_name is required."})

    def save(self, *args, **kwargs):
        self.category = REQUEST_TYPE_TO_CATEGORY.get(self.request_type, "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SupportRequest #{self.pk} - {self.request_type} ({self.status})"


class SupportRequestChatRoom(models.Model):
    support_request = models.OneToOneField(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="chat_room",
    )
    customer_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    operator_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(
        max_length=20,
        choices=ChatRoomStatusChoices.choices,
        default=ChatRoomStatusChoices.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ChatRoom for request #{self.support_request_id}"


class SupportRequestChatMessage(models.Model):
    chat_room = models.ForeignKey(
        SupportRequestChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.CharField(max_length=20, choices=ChatSenderChoices.choices)
    message_type = models.CharField(
        max_length=20,
        choices=ChatMessageTypeChoices.choices,
        default=ChatMessageTypeChoices.TEXT,
    )

    message = models.TextField(blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_maps_url = models.URLField(blank=True)

    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        if self.chat_room.status == ChatRoomStatusChoices.CLOSED:
            raise ValidationError({"chat_room": "This chat room is already closed."})

        if self.message_type == ChatMessageTypeChoices.TEXT:
            if not self.message or not self.message.strip():
                raise ValidationError({"message": "message is required for text messages."})

        if self.message_type == ChatMessageTypeChoices.LOCATION:
            if self.latitude is None or self.longitude is None:
                raise ValidationError({"latitude": "latitude and longitude are required for location messages."})

        if self.message_type == ChatMessageTypeChoices.PHOTO:
            if not self.image:
                raise ValidationError({"image": "image is required for photo messages."})

        if self.message_type == ChatMessageTypeChoices.SYSTEM:
            if not self.message or not self.message.strip():
                raise ValidationError({"message": "message is required for system messages."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message #{self.pk} in room #{self.chat_room_id}"
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models


class AreaChoices(models.TextChoices):
    UENO = "ueno", "Ueno"
    AKIHABARA = "akihabara", "Akihabara"
    YUSHIMA = "yushima", "Yushima"


class CategoryChoices(models.TextChoices):
    DELIVER = "deliver", "Deliver"
    SOMEONE_COMES = "someone_comes", "Someone Comes"


class RequestTypeChoices(models.TextChoices):
    HALAL_FOOD = "halal_food", "I can't find halal food"
    CHOOSE_WHAT_TO_BUY = "choose_what_to_buy", "I don't know what to buy"
    LUGGAGE_HELP = "luggage_help", "I can't move with my luggage"
    SHOW_ME_AROUND = "show_me_around", "Show me around here"


class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    ASSIGNED = "assigned", "Assigned"
    ON_THE_WAY = "on_the_way", "On the way"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


REQUEST_TYPE_TO_CATEGORY = {
    RequestTypeChoices.HALAL_FOOD: CategoryChoices.DELIVER,
    RequestTypeChoices.CHOOSE_WHAT_TO_BUY: CategoryChoices.DELIVER,
    RequestTypeChoices.LUGGAGE_HELP: CategoryChoices.SOMEONE_COMES,
    RequestTypeChoices.SHOW_ME_AROUND: CategoryChoices.SOMEONE_COMES,
}


class SupportRequest(models.Model):
    request_type = models.CharField(max_length=32, choices=RequestTypeChoices.choices)
    category = models.CharField(max_length=32, choices=CategoryChoices.choices, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    area = models.CharField(max_length=32, choices=AreaChoices.choices)
    note = models.TextField(blank=True)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="JPY")
    language = models.CharField(max_length=16, default="en")
    contact_method = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.request_type not in REQUEST_TYPE_TO_CATEGORY:
            raise ValidationError({"request_type": "Unsupported request_type."})
        if self.estimated_price is not None and self.estimated_price < 0:
            raise ValidationError({"estimated_price": "estimated_price must be 0 or greater."})

    def save(self, *args, **kwargs):
        self.category = REQUEST_TYPE_TO_CATEGORY.get(self.request_type, "")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SupportRequest #{self.pk} - {self.request_type} ({self.status})"

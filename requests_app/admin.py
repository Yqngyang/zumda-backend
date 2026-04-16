from django.contrib import admin
from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "request_type",
        "category",
        "area",
        "status",
        "people",
        "estimated_price",
        "created_at",
    )
    list_filter = ("status", "area", "request_type")
    search_fields = ("id", "note", "google_maps_url")
    ordering = ("-created_at",)
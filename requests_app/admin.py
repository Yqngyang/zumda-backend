from django.contrib import admin
from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "request_type", "category", "area", "status", "estimated_price", "created_at")
    list_filter = ("status", "area", "category")
    search_fields = ("id", "request_type", "note", "contact_method", "google_maps_url")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

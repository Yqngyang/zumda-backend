from django.contrib import admin
from django.utils.html import format_html

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
        "open_operator_chat",
    )
    list_filter = ("status", "area", "request_type")
    search_fields = ("id", "customer_name", "note", "google_maps_url")
    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "operator_chat_url",
        "customer_chat_url",
    )

    fieldsets = (
        ("Request", {
            "fields": (
                "request_type",
                "category",
                "customer_name",
                "status",
                "area",
                "people",
                "estimated_price",
                "currency",
                "language",
                "contact_method",
                "note",
            )
        }),
        ("Location", {
            "fields": (
                "latitude",
                "longitude",
                "google_maps_url",
            )
        }),
        ("Chat", {
            "fields": (
                "operator_chat_url",
                "customer_chat_url",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def get_chat_base_url(self):
        return "http://localhost:5500/chat.html"
        # 本番に切り替えるときは:
        # return "https://zumda.app/chat.html"

    def open_operator_chat(self, obj):
        if not hasattr(obj, "chat_room"):
            return "-"
        url = f"{self.get_chat_base_url()}?request_id={obj.id}&token={obj.chat_room.operator_token}"
        return format_html('<a href="{}" target="_blank">Open operator chat</a>', url)

    open_operator_chat.short_description = "Operator chat"

    def operator_chat_url(self, obj):
        if not hasattr(obj, "chat_room"):
            return "-"
        url = f"{self.get_chat_base_url()}?request_id={obj.id}&token={obj.chat_room.operator_token}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    operator_chat_url.short_description = "Operator chat URL"

    def customer_chat_url(self, obj):
        if not hasattr(obj, "chat_room"):
            return "-"
        url = f"{self.get_chat_base_url()}?request_id={obj.id}&token={obj.chat_room.customer_token}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    customer_chat_url.short_description = "Customer chat URL"
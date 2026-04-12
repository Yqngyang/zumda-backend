from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SupportRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("request_type", models.CharField(choices=[
                    ("halal_food", "I can't find halal food"),
                    ("choose_what_to_buy", "I don't know what to buy"),
                    ("luggage_help", "I can't move with my luggage"),
                    ("show_me_around", "Show me around here"),
                ], max_length=32)),
                ("category", models.CharField(choices=[
                    ("deliver", "Deliver"),
                    ("someone_comes", "Someone Comes"),
                ], editable=False, max_length=32)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("area", models.CharField(choices=[
                    ("ueno", "Ueno"),
                    ("akihabara", "Akihabara"),
                    ("yushima", "Yushima"),
                ], max_length=32)),
                ("note", models.TextField(blank=True)),
                ("estimated_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("currency", models.CharField(default="JPY", max_length=3)),
                ("language", models.CharField(default="en", max_length=16)),
                ("contact_method", models.CharField(blank=True, max_length=64)),
                ("status", models.CharField(choices=[
                    ("pending", "Pending"),
                    ("assigned", "Assigned"),
                    ("on_the_way", "On the way"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ], default="pending", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]

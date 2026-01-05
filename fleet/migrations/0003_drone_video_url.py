from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fleet", "0002_drone_api_token_drone_last_alt_drone_last_battery_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="drone",
            name="video_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]

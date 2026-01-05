from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="full_name",
            field=models.CharField(default="", max_length=150),
        ),
        migrations.AddField(
            model_name="profile",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="profiles/"),
        ),
        migrations.AddField(
            model_name="profile",
            name="phone",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="profile",
            name="badge_id",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="profile",
            name="station",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

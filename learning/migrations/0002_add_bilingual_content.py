from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="content_target_language",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="content_english",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="funny_activity_target_language",
            field=models.TextField(blank=True, default=""),
        ),
    ]

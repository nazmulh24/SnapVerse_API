# Generated by Django 5.2.4 on 2025-07-24 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_remove_post_video_alter_post_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_edited",
            field=models.BooleanField(default=False),
        ),
    ]

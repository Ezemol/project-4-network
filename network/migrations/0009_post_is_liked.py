# Generated by Django 5.0.6 on 2024-09-28 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_alter_post_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_liked',
            field=models.BooleanField(default=False),
        ),
    ]

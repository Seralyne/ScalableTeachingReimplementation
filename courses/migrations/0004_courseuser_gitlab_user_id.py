# Generated by Django 5.2.1 on 2025-05-30 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_queuedachievementtoast_received_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseuser',
            name='gitlab_user_id',
            field=models.IntegerField(default=0),
        ),
    ]

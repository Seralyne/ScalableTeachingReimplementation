# Generated by Django 5.2.1 on 2025-05-29 15:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_alter_queuedachievementtoast_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuedachievementtoast',
            name='received_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

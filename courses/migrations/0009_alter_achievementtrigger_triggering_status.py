# Generated by Django 5.2.1 on 2025-05-31 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_alter_courseuser_achievements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievementtrigger',
            name='triggering_status',
            field=models.BooleanField(default=True, verbose_name='Trigger on Test Success'),
        ),
    ]

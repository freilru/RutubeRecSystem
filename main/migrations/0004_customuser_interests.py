# Generated by Django 4.2.16 on 2024-09-28 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_shownvideo'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='interests',
            field=models.JSONField(blank=True, default=list, verbose_name='Интересы'),
        ),
    ]

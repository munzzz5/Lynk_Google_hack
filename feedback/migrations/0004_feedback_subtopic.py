# Generated by Django 4.2.2 on 2024-03-17 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_feedback_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='subtopic',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

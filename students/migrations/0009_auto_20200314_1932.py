# Generated by Django 3.0.3 on 2020-03-14 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_auto_20200314_1739'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ping',
            options={'ordering': ['is_read', '-created_at']},
        ),
        migrations.AddField(
            model_name='ping',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
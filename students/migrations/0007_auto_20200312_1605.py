# Generated by Django 3.0.3 on 2020-03-12 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_auto_20200306_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='matric_number',
            field=models.CharField(max_length=8, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='mobile_number',
            field=models.CharField(max_length=11, null=True, unique=True),
        ),
    ]

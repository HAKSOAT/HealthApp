# Generated by Django 3.0.3 on 2020-03-14 20:51

from django.db import migrations, models
import students.utils.generate


class Migration(migrations.Migration):

    dependencies = [
        ('healthcentre', '0001_initial_manual'),
    ]

    operations = [
        migrations.CreateModel(
            name='IoT',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.CharField(default=students.utils.generate.generate_id, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('board_name', models.CharField(default='ESP32', max_length=50)),
                ('api_key', models.CharField(default='key', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

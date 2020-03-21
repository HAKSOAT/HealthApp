# Generated by Django 3.0.3 on 2020-03-14 15:50

from django.db import migrations, models
import healthcentre.utils.enums
import students.utils.generate


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.CharField(default=students.utils.generate.generate_id, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=8)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[(healthcentre.utils.enums.Roles['worker'], 'worker')], default=healthcentre.utils.enums.Roles['worker'], max_length=15)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
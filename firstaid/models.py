from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

from students.utils.generate import LENGTH_OF_ID, generate_id


class Tip(models.Model):
    class Meta:
        ordering = ['-updated_at', '-views']

    id = models.CharField(
        max_length=LENGTH_OF_ID, primary_key=True,
        default=generate_id, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    ailment = models.CharField(max_length=250, null=False, default='Title')
    symptoms = models.CharField(max_length=2000, null=False, default='Symptoms')
    causes = models.CharField(max_length=2000, null=False, default='Causes')
    dos = models.CharField(max_length=2000, null=False, default='Dos')
    donts = models.CharField(max_length=2000, null=False, default='Don\'ts')
    views = models.PositiveIntegerField(default=0)



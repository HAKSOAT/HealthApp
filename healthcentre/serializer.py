from rest_framework import serializers
from django.contrib.auth.hashers import check_password

from students.models import Student, Ping
from students.utils.generate import LENGTH_OF_OTP
from students.utils.helpers import get_student_fields, check_password_change
from utils.helpers import get_from_redis
from students.utils.enums import Departments
from healthcentre.models import Worker

class PingViewsetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ping
        fields = '__all__'

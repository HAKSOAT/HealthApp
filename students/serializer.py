from rest_framework import serializers
from django.contrib.auth.hashers import check_password

from students.models import Student
from students.utils.generate import LENGTH_OF_OTP
from students.utils.helpers import get_student_fields, update_student, check_choices
from utils.helpers import get_from_redis


class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    last_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    email = serializers.EmailField(required=True, allow_null=False)
    mobile_number = serializers.CharField(min_length=11, max_length=11, required=True, allow_null=False)
    matric_number = serializers.CharField(min_length=8, max_length=8, required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False)

    class Meta:
        model = Student

    def validate(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get('email')
        self.mobile_number = data.get('mobile_number')
        self.password = data.get('password')
        check_choices(data.get('blood_type'), data.get('genotype'),
                      data.get('level'), data.get('department'), data.get('college'))
        return data

    def validate_email(self, email):
        student = Student.objects.filter(email=email).first()
        if student:
            raise serializers.ValidationError(
                'Email already exists'
            )

        return email

    def validate_matric_number(self, matric_number):
        student = Student.objects.filter(matric_number=matric_number).first()
        if student:
            raise serializers.ValidationError(
                'Matric number already exists'
            )

        return matric_number

    def validate_mobile_number(self, mobile_number):
        student = Student.objects.filter(mobile_number=mobile_number).first()
        if student:
            raise serializers.ValidationError(
                'Mobile number already exists'
            )

        return mobile_number

    def create(self, data):
        allowed_student_fields = set(get_student_fields())
        passed_student_fields = set(data.keys())
        invalid_fields = passed_student_fields - allowed_student_fields
        for field in invalid_fields:
            data.pop(field)
        student = Student(**data)
        student.email = data['email'].lower()
        student.set_password(data['password'])
        student.save()
        return student


class ConfirmStudentSerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=LENGTH_OF_OTP, allow_null=False, required=True)
    email = serializers.EmailField(required=True, allow_null=False, min_length=5)
    new_otp = serializers.BooleanField(default=False)

    def validate(self, data):
        self.email = data.get('email')
        student = Student.objects.filter(email=self.email.lower()).first()
        if not student:
            raise serializers.ValidationError(
                'Student does not have an account'
            )

        if student.is_confirmed:
            raise serializers.ValidationError(
                'Student\'s account is already confirmed'
            )

        self.new_otp = data.get('new_otp')
        if not self.new_otp:
            self.otp = data.get('otp')
            otp = get_from_redis(f'OTP: {self.email}')
            if self.otp != otp:
                raise serializers.ValidationError(
                    'OTP code is invalid or expired'
                )

        return data

    def update(self, student, *args):
        student.is_confirmed = True
        student.save()
        return student


class LoginStudentSerializer(serializers.Serializer):
    user = serializers.CharField(allow_null=False, required=True)
    password = serializers.CharField(allow_null=False, required=True)

    def validate(self, data):
        self.user = data.get('user')
        student = Student.objects.filter(matric_number=self.user).first() or\
                  Student.objects.filter(email=self.user.lower()).first()
        if not student:
            raise serializers.ValidationError(
                'Account does not exist'
            )

        if not student.is_confirmed:
            raise serializers.ValidationError(
                'Account is not confirmed'
            )

        self.password = data.get('password')
        password_valid = check_password(self.password, student.password)
        if not password_valid:
            raise serializers.ValidationError(
                'Wrong password'
            )

        data['user_id'] = student.id
        return data


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        student_fields = get_student_fields()
        student_fields.remove('password')
        fields = student_fields

    def validate(self, student, data):
        data = update_student(student, data)
        if data.get('errors', None):
            raise serializers.ValidationError(data)
        return data

    def update(self, student, validated_data):
        allowed_student_fields = set(get_student_fields(new='new_password'))
        passed_student_fields = set(validated_data.keys())
        invalid_fields = passed_student_fields - allowed_student_fields

        for field in invalid_fields:
            validated_data.pop(field)

        Student.objects.update_or_create(
            id=student.id,
            defaults=validated_data
        )

        if validated_data.get('new_password'):
            student.set_password(validated_data['new_password'])
            student.save()
        return validated_data
from rest_framework import serializers
from django.contrib.auth.hashers import check_password

from students.models import Student, Ping
from students.utils.generate import LENGTH_OF_OTP
from students.utils.helpers import get_student_fields, check_password_change
from utils.helpers import get_from_redis
from students.utils.enums import Departments
from healthcentre.models import Worker
from students.utils.serializer_checks import RegisterStudent


class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    email = serializers.CharField(default='')
    password = serializers.CharField(default='')

    class Meta:
        model = Student

    def validate_first_name(self, first_name):
        first_name = RegisterStudent.check_name(first_name, 'First name')
        return first_name

    def validate_last_name(self, last_name):
        last_name = RegisterStudent.check_name(last_name, 'Last name')
        return last_name

    def validate_email(self, email):
        email = RegisterStudent.check_email(email)
        student = Student.objects.filter(email=email).first()
        if student:
            raise serializers.ValidationError('Email already exists')
        return email

    def create(self, data):
        student = Student(**data)
        student.email = data['email'].lower()
        student.set_password(data['password'])
        student.save()
        return student


class ConfirmStudentSerializer(serializers.Serializer):
    otp = serializers.CharField(default='')

    def validate_otp(self, otp):
        if otp:
            cached_otp = get_from_redis(
                f'CONFIRM: {self.context.get("email")}', None)
            if otp != cached_otp:
                raise serializers.ValidationError(
                    'OTP is invalid or expired'
                )

        return otp

    def update(self, student, *args):
        student.is_confirmed = True
        student.save()
        return student


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(allow_null=False, required=True)
    password = serializers.CharField(allow_null=False, required=True)

    def validate(self, data):
        if self.context.get('user_type') == 'student':
            user = Student.objects.filter(
                email=data.get('email').lower()).first()
        elif self.context.get('user_type') == 'healthcentre':
            user = Worker.objects.filter(
                username=data.get('email').lower()).first()

        if not user:
            raise serializers.ValidationError(
                {'email': 'Account does not exist'}
            )

        if isinstance(user, Student):
            if not user.is_confirmed:
                raise serializers.ValidationError(
                    {'email': 'Account is not yet confirmed'}
                )

        password_valid = check_password(data.get('password'), user.password)
        if not password_valid:
            raise serializers.ValidationError(
                {'password': 'Wrong password'}
            )

        data['user'] = user
        return data


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        min_length=2, allow_null=False, required=True)
    last_name = serializers.CharField(
        min_length=2, allow_null=False, required=True)
    email = serializers.EmailField(
        required=True, allow_null=False)
    password = serializers.CharField(
        required=True, allow_null=False)
    mobile_number = serializers.CharField(
        min_length=11, max_length=11, allow_null=False)
    matric_number = serializers.CharField(
        min_length=8, max_length=8, allow_null=False)
    clinic_number = serializers.CharField(
        min_length=8, required=False)
    image = serializers.URLField(
        required=False)
    department = serializers.ChoiceField(
        choices=[dpt.value for dpt in Departments], required=False)
    new_password = serializers.CharField(
        required=False, allow_null=False)

    class Meta:
        model = Student
        student_fields = get_student_fields()
        # The ModelSerializer requires new_password
        # This is because of the new_password variable defined above
        student_fields.append('new_password')
        fields = student_fields

    def validate(self, data):
        student = Student.objects.filter(id=self.context.get('id')).first()
        password_errors = check_password_change(student,
                                                data.get('password'),
                                                data.get('new_password'))
        if password_errors:
            raise serializers.ValidationError(password_errors)
        return data

    def validate_email(self, email):
        student = Student.objects.filter(email=email).first()
        if student:
            raise serializers.ValidationError(
                {'email': 'Email already exists'}
            )

        return email

    def validate_matric_number(self, matric_number):
        student = Student.objects.filter(
            matric_number=matric_number).exclude(
            id=self.context.get('id')).first()
        if student:
            raise serializers.ValidationError(
                {'matric_number': 'Matric number already exists'}
            )

        return matric_number

    def validate_mobile_number(self, mobile_number):
        student = Student.objects.filter(
            mobile_number=mobile_number).exclude(
            id=self.context.get('id')).first()
        if student:
            raise serializers.ValidationError(
                {'mobile_number': 'Mobile number already exists'}
            )

        return mobile_number

    def validate_clinic_number(self, clinic_number):
        if clinic_number:
            student = Student.objects.filter(
                clinic_number=clinic_number).exclude(
                id=self.context.get('id')).first()
            if student:
                raise serializers.ValidationError(
                    {'clinic_number': 'Clinic number already exists'}
                )

        return clinic_number

    def update(self, student, validated_data):
        if validated_data.get('new_password'):
            student.set_password(validated_data['new_password'])
            student.save()
            validated_data.pop('new_password')
            validated_data.pop('password')
        Student.objects.filter(id=student.id).update(**validated_data)
        return validated_data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(min_length=LENGTH_OF_OTP, required=False)
    password = serializers.CharField(required=False)
    password_again = serializers.CharField(required=False)

    def validate(self, data):
        if data.get('otp'):
            otp = data.get('otp')
            cached_otp = get_from_redis(f'RESET: {data.get("email")}', None)
            if otp != cached_otp:
                raise serializers.ValidationError(
                    {'otp': 'OTP code is invalid or expired'}
                )
        else:
            return data

        if not data.get('password') and data.get('password_again'):
            raise serializers.ValidationError(
                {'password': 'This value can\'t be null since password_again was provided'}
            )

        if not data.get('password_again') and data.get('password'):
            raise serializers.ValidationError(
                {'password_again': 'This value can\'t be null since password was provided'}
            )

        if data.get('password') and data.get('password_again'):
            if data.get('password') != data.get('password_again'):
                raise serializers.ValidationError(
                    {'password': 'password and password_again fields must have the same values'}
                )

        return data

    def validate_email(self, email):
        student = Student.objects.filter(email=email).first()
        if not student:
            raise serializers.ValidationError(
                {'email': 'Student does not have an account'}
            )
        if not student.is_confirmed:
            raise serializers.ValidationError(
                {'email': 'Account is not yet confirmed'}
            )
        return student

    def update(self, student, data):
        student.set_password(data.get('password'))
        student.save()
        return student


class PingViewsetSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255, allow_null=False)
    location = serializers.CharField(required=False)

    def validate(self, data):
        errors = {}
        student = Student.objects.filter(id=self.context.get('id')).first()
        if not student.matric_number:
            errors['matric_number'] = \
                'Value must be set before ping works'
        if not student.clinic_number:
            errors['clinic_number'] = \
                'Value must be set before ping works'
        if not student.mobile_number:
            errors['mobile_number'] = \
                'Value must be set before ping works'
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        student = Student.objects.filter(id=self.context.get('id')).first()
        ping_data = {
            'message': validated_data.get('message'),
            'location': validated_data.get('location'),
            'student': student
        }
        ping = Ping(**ping_data)
        ping.save()
        return ping

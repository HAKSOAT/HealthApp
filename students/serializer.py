from rest_framework import serializers
from django.contrib.auth.hashers import check_password

from students.models import Student, Ping
from students.utils.generate import LENGTH_OF_OTP
from students.utils.helpers import get_student_fields, check_password_change
from utils.helpers import get_from_redis
from students.utils.enums import Departments
from healthcentre.models import Worker
from students.utils.serializer_checks import StudentChecker


class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    email = serializers.CharField(default='')
    password = serializers.CharField(default='')

    class Meta:
        model = Student

    def validate_first_name(self, first_name):
        first_name = StudentChecker.check_name(first_name, 'First name')
        return first_name

    def validate_last_name(self, last_name):
        last_name = StudentChecker.check_name(last_name, 'Last name')
        return last_name

    def validate_email(self, email):
        email = StudentChecker.check_email(email)
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
    email = serializers.CharField(default='')
    password = serializers.CharField(default='')

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
                    {'id': user.id,
                     'email': 'Account is not yet confirmed. '
                              'Kindly confirm first.'}
                )

        password_valid = check_password(data.get('password'), user.password)
        if not password_valid:
            raise serializers.ValidationError(
                {'password': 'Wrong password'}
            )

        data['user'] = user
        return data


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')
    email = serializers.CharField(default='')
    password = serializers.CharField(default='')
    mobile_number = serializers.CharField(default='')
    matric_number = serializers.CharField(default='')
    clinic_number = serializers.CharField(default='')
    image = serializers.CharField(default='')
    department = serializers.CharField(default='')
    new_password = serializers.CharField(default='')

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

    def validate_first_name(self, first_name):
        if first_name:
            first_name = StudentChecker.check_name(first_name, 'First name')
        return first_name

    def validate_last_name(self, last_name):
        if last_name:
            last_name = StudentChecker.check_name(last_name, 'First name')
        return last_name

    def validate_email(self, email):
        if email:
            email = StudentChecker.check_email(email)
            student = Student.objects.filter(email=email).first()
            if student:
                raise serializers.ValidationError('Email already exists')

        return email

    def validate_matric_number(self, matric_number):
        if matric_number:
            matric_number = StudentChecker.check_matric_number(matric_number)
            student = Student.objects.filter(
                matric_number=matric_number).exclude(
                id=self.context.get('id')).first()
            if student:
                raise serializers.ValidationError(
                    'Matric number already exists')

        return matric_number

    def validate_mobile_number(self, mobile_number):
        if mobile_number:
            mobile_number = StudentChecker.check_mobile_number(mobile_number)
            student = Student.objects.filter(
                mobile_number=mobile_number).exclude(
                id=self.context.get('id')).first()
            if student:
                raise serializers.ValidationError(
                    'Mobile number already exists'
                )

        return mobile_number

    def validate_clinic_number(self, clinic_number):
        if clinic_number:
            clinic_number = StudentChecker.check_clinic_number(clinic_number)
            student = Student.objects.filter(
                clinic_number=clinic_number).exclude(
                id=self.context.get('id')).first()
            if student:
                raise serializers.ValidationError(
                    'Clinic number already exists'
                )

        return clinic_number

    def validate_department(self, department):
        if department:
            department = StudentChecker.check_department_number(department)
        return department

    def update(self, student, validated_data):
        if validated_data.get('new_password'):
            student.set_password(validated_data['new_password'])
            student.save()
            validated_data.pop('new_password')
            validated_data.pop('password')
        Student.objects.filter(id=student.id).update(**validated_data)
        return validated_data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(default='')
    otp = serializers.CharField(default='')
    password = serializers.CharField(default='')
    password_again = serializers.CharField(default='')

    def validate(self, data):
        if data.get('otp'):
            otp = data.get('otp')
            print(data)
            print(data.get("email"))
            cached_otp = get_from_redis(f'RESET: {data.get("email")}', None)
            if otp != cached_otp:
                raise serializers.ValidationError(
                    {'otp': 'OTP code is invalid or expired'}
                )
        else:
            return data

        if not data.get('password') and data.get('password_again'):
            raise serializers.ValidationError(
                {'password': 'Password is required'}
            )

        if not data.get('password_again') and data.get('password'):
            raise serializers.ValidationError(
                {'password_again': 'Confirmation password is required'}
            )

        if data.get('password') and data.get('password_again'):
            if data.get('password') != data.get('password_again'):
                raise serializers.ValidationError(
                    {'password': 'Password and confirmation password'
                                 ' should be the same'}
                )

        return data

    def validate_email(self, email):
        email = StudentChecker.check_email(email)
        student = Student.objects.filter(email=email).first()
        if not student:
            raise serializers.ValidationError(
                'Account does not exist')
        if not student.is_confirmed:
            raise serializers.ValidationError('Account is not yet confirmed')
        return email

    def update(self, student, data):
        student.set_password(data.get('password'))
        student.save()
        return student


class PingViewsetSerializer(serializers.ModelSerializer):
    message = serializers.CharField(default='')
    location = serializers.CharField(default='')

    class Meta:
        model = Ping
        fields = ['id', 'message', 'location', 'created_at']

    def validate(self, data):
        errors = {}
        student = Student.objects.filter(id=self.context.get('id')).first()
        if not student.matric_number:
            errors['matric_number'] = \
                'You can only send ping after adding matric number to profile'
        if not student.clinic_number:
            errors['clinic_number'] = \
                'You can only send ping after adding clinic number to profile'
        if not student.mobile_number:
            errors['mobile_number'] = \
                'You can only send ping after adding mobile number to profile'
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def validate_message(self, message):
        max_message_length = 255
        min_message_length = 10
        if len(message) < min_message_length:
            raise serializers.ValidationError(
                'Message has to be more than 10 characters'
            )
        elif len(message) > max_message_length:
            raise serializers.ValidationError(
                'Message has to be less than 255 characters'
            )
        return message

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

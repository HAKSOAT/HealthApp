from rest_framework import serializers
from django.contrib.auth.hashers import check_password

from students.models import Student
from students.utils.generate import LENGTH_OF_OTP
from students.utils.helpers import get_student_fields, check_password_change
from utils.helpers import get_from_redis
from students.utils.enums import BloodTypes, GenoTypes, StudentLevels, Departments, Colleges


class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    last_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    email = serializers.EmailField(required=True, allow_null=False)
    mobile_number = serializers.CharField(min_length=11, max_length=11, required=True, allow_null=False)
    matric_number = serializers.CharField(min_length=8, max_length=8, required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False)
    blood_type = serializers.ChoiceField(choices=[bt.value for bt in BloodTypes], required=False)
    genotype = serializers.ChoiceField(choices=[gt.value for gt in GenoTypes], required=False)
    level = serializers.ChoiceField(choices=[lev.value for lev in StudentLevels], required=False)
    department = serializers.ChoiceField(choices=[dpt.value for dpt in Departments], required=False)
    college = serializers.ChoiceField(choices=[col.value for col in Colleges], required=False)

    class Meta:
        model = Student

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
        student = Student.objects.filter(email=data.get('email').lower()).first()
        if not student:
            raise serializers.ValidationError(
                'Student does not have an account'
            )

        if student.is_confirmed:
            raise serializers.ValidationError(
                'Student\'s account is already confirmed'
            )

        if not data.get('new_otp'):
            otp = data.get('otp')
            cached_otp = get_from_redis(f'OTP: {data.get("email")}')
            if otp != cached_otp:
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
        student = Student.objects.filter(matric_number=data.get('user')).first() or\
                  Student.objects.filter(email=data.get('user').lower()).first()
        if not student:
            raise serializers.ValidationError(
                'Account does not exist'
            )

        if not student.is_confirmed:
            raise serializers.ValidationError(
                'Account is not confirmed'
            )

        password_valid = check_password(data.get('password'), student.password)
        if not password_valid:
            raise serializers.ValidationError(
                'Wrong password'
            )

        data['student_id'] = student.id
        return data


class StudentSerializer(RegisterStudentSerializer):
    new_password = serializers.CharField(required=False, allow_null=False)

    class Meta:
        model = Student
        student_fields = get_student_fields()
        student_fields.remove('password')
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
        if email:
            raise serializers.ValidationError(
                'Email can\'t be updated'
            )
        return email

    def validate_matric_number(self, matric_number):
        print(matric_number)
        if matric_number:
            raise serializers.ValidationError(
                'Matric number can\'t be updated'
            )
        return matric_number

    def validate_mobile_number(self, mobile_number):
        if mobile_number:
            raise serializers.ValidationError(
                'Mobile number can\'t be updated'
            )
        return mobile_number

    def update(self, student, validated_data):
        Student.objects.update_or_create(
            id=student.id,
            defaults=validated_data
        )
        if validated_data.get('new_password'):
            student.set_password(validated_data['new_password'])
            student.save()
        return validated_data

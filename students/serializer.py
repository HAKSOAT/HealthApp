from rest_framework import serializers

from students.models import Student


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
        student = Student(**data)
        student.save()
        return student



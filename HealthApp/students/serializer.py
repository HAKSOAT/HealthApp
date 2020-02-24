from rest_framework import serializers

from students.models import Student


class RegisterStudentSerializer(serializers.Serializer):
    first_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    last_name = serializers.CharField(min_length=2, allow_null=False, required=True)
    email = serializers.EmailField(required=True, allow_null=False)
    mobile_number = serializers.CharField(min_length=11, max_length=11, required=True, allow_null=False)

    def validate(self, data):
        self.first_name = data.get('first_name')
        self.last_name = data.get('last_name')
        self.email = data.get('email')
        self.mobile_number = data.get('mobile_number')
        return data

    def create(self, data):
        student = Student(**data)
        student.save()
        return student



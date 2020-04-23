from rest_framework import serializers

from students.models import Student, Ping


class PingViewsetSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model = Ping
        ref_name = 'HealthcentrePingViewsetSerializer'
        fields = ['id', 'message', 'location', 'created_at', 'student',
                  'status']

    def get_student(self, ping):
        student_id = ping.student.id
        student = Student.objects.filter(id=student_id).first()
        data = {
            'first_name': student.first_name,
            'last_name': student.last_name,
            'id': student_id,
            'image': student.image
        }
        return data

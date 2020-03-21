from rest_framework import serializers

from students.models import Student, Ping


class PingViewsetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ping
        fields = ['id', 'message', 'location', 'created_at']

from rest_framework import serializers

from firstaid.models import Tip


class FirstAidTipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tip
        fields = "__all__"

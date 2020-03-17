import string
import re

from rest_framework import serializers

class RegisterStudent:
    @staticmethod
    def check_name(name, name_type):
        if len(name) < 3:
            raise serializers.ValidationError(
                f'{name_type} should have more than two characters'
            )

        if set(name).difference(string.ascii_letters, {' '}):
            raise serializers.ValidationError(
                f'{name_type} can only allow English alphabets'
            )

        return name

    @staticmethod
    def check_email(email):
        pattern = re.match(r'^[^@\s]+@[^@\s]+\.[^@]+$', email)
        if not pattern:
            raise serializers.ValidationError(
                f'Email is invalid'
            )

        return email

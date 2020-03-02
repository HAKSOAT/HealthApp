import uuid
from django.utils.http import int_to_base36

LENGTH_OF_ID = 12

LENGTH_OF_OTP = 5


def generate_id():
    """Generates an random strings with the defined LENGTH_OF_ID"""
    return int_to_base36(uuid.uuid4().int)[:LENGTH_OF_ID]


def generate_otp():
    """Generates an random strings from 0-9 with the defined LENGTH_OF_OTP"""
    return str(uuid.uuid4().int)[:LENGTH_OF_OTP]

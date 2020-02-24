import uuid
from django.utils.http import int_to_base36

LENGTH_OF_ID = 12


def generate_id():
    """Generates an random strings with the defined LENGTH_OF_ID"""
    return int_to_base36(uuid.uuid4().int)[:LENGTH_OF_ID]

from django.core.cache import cache


def save_in_redis(key, data, timeout):
    """
        This function save in redis
        1. This function take three arguments: key,
            data to be saved and timeout value
        2. Save the data with {key} arg as the key in redis
    """
    cache.set(key, data, timeout=timeout)


def get_from_redis(key):
    """
        This function save in redis
        1. This function takes one argument: key
        2. Retrieves the data cached using key or None
    """
    cache.get(key)

import django.dispatch

ping_signal = django.dispatch.Signal(providing_args=["ping_data"])

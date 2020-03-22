from django.apps import AppConfig


class HealthcentreConfig(AppConfig):
    name = 'healthcentre'

    def ready(self):
        import healthcentre.receivers

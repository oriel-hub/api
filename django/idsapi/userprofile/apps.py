from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    name = 'userprofile'

    def ready(self):
        from . import signals  # noqa

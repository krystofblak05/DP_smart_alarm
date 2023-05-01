#from turtle import update
from django.apps import AppConfig


class SmartAlarmAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'smart_alarm_app'

    def ready(self):
        print("Updater spuštěn")
        from .scheduler import updater
        updater.start()

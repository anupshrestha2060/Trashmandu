from django.apps import AppConfig


class CollectorappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectorapp'
def ready(self):
    import collectorapp.signals

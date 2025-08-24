from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms'

    def ready(self):
        """
        Import and register signals when the app is ready.
        This ensures signals are connected when Django starts.
        """
        import cms.signals

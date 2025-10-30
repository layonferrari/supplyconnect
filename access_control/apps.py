from django.apps import AppConfig


class AccessControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'access_control'
    verbose_name = 'Controle de Acesso'
    
    def ready(self):
        """Importa signals quando o app estiver pronto."""
        try:
            import access_control.signals  # noqa
        except ImportError:
            pass
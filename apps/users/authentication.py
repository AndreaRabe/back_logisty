from django.contrib.auth.backends import ModelBackend
from django.utils.timezone import now


class AdminAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and user.is_superuser:  # Vérifier si l'utilisateur est un admin
            user.last_admin_login = now()
            user.save(update_fields=['last_admin_login'])
        return user

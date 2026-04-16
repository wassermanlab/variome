import logging

from django.contrib.auth import login
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class AlwaysLoggedInMiddleware:
    """
    Middleware that automatically logs in anonymous users as the public demo
    user when PUBLIC_BVL is enabled, allowing unauthenticated access to the
    site while keeping the admin area protected.

    Requires the public demo user (username='public_demo_user',
    email='public_demo_user@ibvl.ca') to exist in the database.
    If the user does not exist, a warning is logged and public access is
    effectively disabled.
    """

    _user_missing_warned = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            and not request.path.startswith("/admin")
        ):
            try:
                user = User.objects.get(
                    username="public_demo_user",
                    email="public_demo_user@ibvl.ca",
                )
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
            except User.DoesNotExist:
                if not AlwaysLoggedInMiddleware._user_missing_warned:
                    logger.warning(
                        "PUBLIC_BVL is set to True but the public demo user "
                        "(username='public_demo_user', "
                        "email='public_demo_user@ibvl.ca') "
                        "does not exist. Public access is disabled. "
                        "Create this user to enable public access."
                    )
                    AlwaysLoggedInMiddleware._user_missing_warned = True
        return self.get_response(request)

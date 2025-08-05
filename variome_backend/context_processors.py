from django.conf import settings


def custom_admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {
            # workaround fixes: the built-in context variable "site_url" gets erased
            # when there is an __init__.py file in the admin folder
            "frontend_url": settings.SITE_URL
        }
    else:
        return {}

# decorators.py
from django.http import HttpResponseForbidden
from .alert_module import notify_access_limit_reached


def access_count_gate():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            limit = request.user.profile.accesses_per_day
            count = request.user.profile.access_count
            if count > limit:
                try:
                    notify_access_limit_reached(request.user, limit)
                except Exception as e:
                    print(e)
                return HttpResponseForbidden(status=429)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

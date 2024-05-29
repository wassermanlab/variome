
# decorators.py
from django.http import HttpResponseForbidden

def access_count_gate():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            limit = request.user.profile.accesses_per_day
            count = request.user.profile.access_count
            if count > limit:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
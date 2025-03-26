# Import views from folder
from .authentication import *
from .profile_view import profile_view_redirect, profile_view_json, profile_view_stub
from .login_views import login_failed, login, admin_login, logout_view, LoginRedirectView
from .tracking_dashboard import tracking_dashboard

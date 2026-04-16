from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from variome_backend.middleware import AlwaysLoggedInMiddleware


class AlwaysLoggedInMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=MagicMock())
        # Reset the class-level warning flag between tests
        AlwaysLoggedInMiddleware._user_missing_warned = False

    def _make_middleware(self):
        return AlwaysLoggedInMiddleware(self.get_response)

    def _make_request(self, path="/api/variant/"):
        request = self.factory.get(path)
        # Simulate an anonymous user
        request.user = MagicMock()
        request.user.is_authenticated = False
        return request

    def _create_public_user(self):
        user = User(username="public_demo_user", email="public_demo_user@ibvl.ca")
        user.set_unusable_password()
        user.save()
        return user

    def test_logs_in_public_user_when_exists(self):
        """Anonymous users are logged in as public_demo_user when it exists."""
        public_user = self._create_public_user()
        middleware = self._make_middleware()
        request = self._make_request()

        with patch("variome_backend.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_called_once()
            called_user = mock_login.call_args[0][1]
            self.assertEqual(called_user.pk, public_user.pk)

    def test_skips_login_for_admin_path(self):
        """Admin paths are never auto-logged-in."""
        self._create_public_user()
        middleware = self._make_middleware()
        request = self._make_request(path="/admin/")

        with patch("variome_backend.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_not_called()

    def test_no_login_when_user_missing(self):
        """No login attempt and a warning is logged when public user is absent."""
        middleware = self._make_middleware()
        request = self._make_request()

        with patch("variome_backend.middleware.login") as mock_login, \
             patch("variome_backend.middleware.logger") as mock_logger:
            middleware(request)
            mock_login.assert_not_called()
            mock_logger.warning.assert_called_once()

    def test_warning_logged_only_once(self):
        """The missing-user warning is only logged once across multiple requests."""
        middleware = self._make_middleware()

        with patch("variome_backend.middleware.login"), \
             patch("variome_backend.middleware.logger") as mock_logger:
            middleware(self._make_request())
            middleware(self._make_request())
            self.assertEqual(mock_logger.warning.call_count, 1)

    def test_authenticated_user_not_replaced(self):
        """Already authenticated users are left alone."""
        self._create_public_user()
        middleware = self._make_middleware()
        request = self._make_request()
        request.user.is_authenticated = True

        with patch("variome_backend.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_not_called()

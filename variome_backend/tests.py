from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from variome_backend.library.models import GenomicGnomadFrequency, Variant
from variome_backend.library.views.variant import get_gnomad_toolbox_frequencies
from variome_backend.library_access.middleware import AlwaysLoggedInMiddleware


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

        with patch("variome_backend.library_access.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_called_once()
            called_user = mock_login.call_args[0][1]
            self.assertEqual(called_user.pk, public_user.pk)

    def test_skips_login_for_admin_path(self):
        """Admin paths are never auto-logged-in."""
        self._create_public_user()
        middleware = self._make_middleware()
        request = self._make_request(path="/admin/")

        with patch("variome_backend.library_access.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_not_called()

    def test_no_login_when_user_missing(self):
        """No login attempt and a warning is logged when public user is absent."""
        middleware = self._make_middleware()
        request = self._make_request()

        with patch("variome_backend.library_access.middleware.login") as mock_login, \
             patch("variome_backend.library_access.middleware.logger") as mock_logger:
            middleware(request)
            mock_login.assert_not_called()
            mock_logger.warning.assert_called_once()

    def test_warning_logged_only_once(self):
        """The missing-user warning is only logged once across multiple requests."""
        middleware = self._make_middleware()

        with patch("variome_backend.library_access.middleware.login"), \
             patch("variome_backend.library_access.middleware.logger") as mock_logger:
            middleware(self._make_request())
            middleware(self._make_request())
            self.assertEqual(mock_logger.warning.call_count, 1)

    def test_authenticated_user_not_replaced(self):
        """Already authenticated users are left alone."""
        self._create_public_user()
        middleware = self._make_middleware()
        request = self._make_request()
        request.user.is_authenticated = True

        with patch("variome_backend.library_access.middleware.login") as mock_login:
            middleware(request)
            mock_login.assert_not_called()


class GnomadToolboxFrequencyTests(TestCase):
    @patch(
        "gnomad_toolbox.filtering.variant.get_single_variant",
        return_value=MagicMock(
            take=MagicMock(
                return_value=[
                    {
                        "freq": [
                            {
                                "AF": 0.9,
                                "AC": 137076,
                                "AN": 152210,
                                "homozygote_count": 61788,
                                "hemizygote_count": 0,
                            }
                        ]
                    }
                ]
            )
        ),
    )
    @patch("hail.current_backend")
    def test_returns_all_gnomad_frequency_fields(
        self, mock_current_backend, mock_get_single_variant
    ):
        frequencies = get_gnomad_toolbox_frequencies("22-27039615-T-C")

        self.assertEqual(
            frequencies,
            {
                "af_tot": "0.9000000000",
                "ac_tot": 137076,
                "an_tot": 152210,
                "hom_tot": 61788,
                "hemi_tot": 0,
            },
        )
        mock_get_single_variant.assert_called_once_with(
            variant="22-27039615-T-C",
            data_type="joint",
            version="4.1",
        )

    @patch(
        "variome_backend.library.views.variant.get_gnomad_toolbox_frequencies",
        side_effect=RuntimeError,
    )
    def test_uses_local_gnomad_frequencies_when_toolbox_fails(self, mock_frequencies):
        variant = Variant.objects.create(variant_id="22-27039615-T-C", var_type="SNV")
        frequency = GenomicGnomadFrequency.objects.create(
            variant=variant,
            af_tot="0.9005720000",
            ac_tot=137076,
            an_tot=152210,
            hom_tot=61788,
            hemi_tot=0,
        )

        from variome_backend.library.views.variant import (
            gnomad_frequencies as gnomad_frequencies_view,
        )

        request = RequestFactory().get(
            "/api/gnomad-frequencies", {"variant": variant.variant_id}
        )
        request.user = MagicMock(
            is_authenticated=True,
            profile=MagicMock(access_count=0, accesses_per_day=1),
        )
        response = gnomad_frequencies_view(request)

        self.assertEqual(response.data["gnomadFrequencies"]["id"], frequency.id)
        self.assertIn(
            "gnomAD toolbox unavailable; using locally stored gnomAD frequencies",
            response.data["errors"],
        )

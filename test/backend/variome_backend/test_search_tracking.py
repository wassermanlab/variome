from datetime import timedelta

from auditlog.models import LogEntry
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from variome_backend.library_access.models import SearchQueryAction


class InvalidSearchTracking(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="search-user")
        self.client.force_login(self.user)
        self.url = reverse("invalid_search_query")

    def test_client_rejected_query_is_tracked_without_identity(self):
        before = timezone.now()
        response = self.client.post(
            self.url,
            {
                "query": "<script>alert('query')</script>",
                "selectedAssembly": "GRCh38",
                "user": self.user.pk,
                "is_valid": True,
                "result_count": 123,
                "chromosome": "1",
                "position": 1000,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        action = SearchQueryAction.objects.get()
        self.assertEqual(action.query, "<script>alert('query')</script>")
        self.assertEqual(action.reference_genome, "GRCh38")
        self.assertFalse(action.is_valid)
        self.assertEqual(action.result_count, 0)
        self.assertIsNone(action.chromosome)
        self.assertIsNone(action.position)
        self.assertGreaterEqual(action.created_at, before)
        self.assertLessEqual(action.created_at, timezone.now())
        self.assertFalse(any(field.is_relation for field in action._meta.fields))
        content_type = ContentType.objects.get_for_model(SearchQueryAction)
        self.assertFalse(LogEntry.objects.filter(content_type=content_type).exists())

    def test_repeated_searches_are_separate_actions(self):
        for _ in range(2):
            response = self.client.post(
                self.url, {"query": "invalid"}, content_type="application/json"
            )
            self.assertEqual(response.status_code, 201)
        self.assertEqual(SearchQueryAction.objects.count(), 2)

    def test_endpoint_requires_authentication_and_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.client.logout()
        response = self.client.post(
            self.url, {"query": "invalid"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SearchQueryAction.objects.exists())

    def test_endpoint_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(
            self.url, {"query": "invalid"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SearchQueryAction.objects.exists())

    def test_endpoint_accepts_profile_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        profile = client.get("/api/user/").json()
        response = client.post(
            self.url,
            {"query": "invalid"},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=profile["user"]["csrf_token"],
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SearchQueryAction.objects.get().query, "invalid")

    def test_malformed_payloads_do_not_create_actions(self):
        for payload in [
            {},
            {"query": None},
            {"query": {}},
            {"query": "x", "selectedAssembly": "x" * 33},
        ]:
            with self.subTest(payload=payload):
                response = self.client.post(
                    self.url, payload, content_type="application/json"
                )
                self.assertEqual(response.status_code, 400)
        self.assertFalse(SearchQueryAction.objects.exists())


class SearchQueryAnalytics(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dashboard-user", is_staff=True)
        self.client.force_login(self.user)
        self.url = reverse("search_query_actions")

    def grant_dashboard_access(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_tracking_dashboard")
        )

    def test_analytics_require_dashboard_permission(self):
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.grant_dashboard_access()
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_paginated_results_are_newest_first_and_anonymous(self):
        self.grant_dashboard_access()
        for index in range(51):
            SearchQueryAction.objects.create(query=f"query-{index}", is_valid=True)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 51)
        self.assertEqual(data["pages"], 2)
        self.assertEqual(len(data["results"]), 50)
        self.assertEqual(data["results"][0]["query"], "query-50")
        self.assertEqual(
            set(data["results"][0]),
            {
                "query",
                "created_at",
                "reference_genome",
                "result_count",
                "is_valid",
                "chromosome",
                "position",
            },
        )
        second_page = self.client.get(self.url, {"page": 2}).json()
        self.assertEqual([row["query"] for row in second_page["results"]], ["query-0"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(data["page_size"], 50)

    def test_custom_page_size_and_date_sorting(self):
        self.grant_dashboard_access()
        for index in range(5):
            action = SearchQueryAction.objects.create(
                query=f"query-{index}", is_valid=True
            )
            SearchQueryAction.objects.filter(pk=action.pk).update(
                created_at=timezone.now() - timedelta(days=5 - index)
            )

        for sort, queries in [
            ("oldest", ["query-0", "query-1"]),
            ("newest", ["query-4", "query-3"]),
        ]:
            with self.subTest(sort=sort):
                data = self.client.get(self.url, {"page_size": 2, "sort": sort}).json()
                self.assertEqual(data["page_size"], 2)
                self.assertEqual(data["count"], 5)
                self.assertEqual(data["pages"], 3)
                self.assertEqual([row["query"] for row in data["results"]], queries)

        last_page = self.client.get(
            self.url, {"page": 3, "page_size": 2, "sort": "oldest"}
        ).json()
        self.assertEqual([row["query"] for row in last_page["results"]], ["query-4"])

    def test_date_sorting_is_stable_for_identical_timestamps(self):
        self.grant_dashboard_access()
        for query in ["first", "second", "third"]:
            SearchQueryAction.objects.create(query=query, is_valid=True)
        SearchQueryAction.objects.update(created_at=timezone.now())
        for sort, expected in [
            ("oldest", ["first", "second", "third"]),
            ("newest", ["third", "second", "first"]),
        ]:
            queries = [
                self.client.get(
                    self.url, {"sort": sort, "page_size": 1, "page": page}
                ).json()["results"][0]["query"]
                for page in range(1, 4)
            ]
            self.assertEqual(queries, expected)

    def test_coordinate_data_and_legacy_records(self):
        self.grant_dashboard_access()
        SearchQueryAction.objects.create(
            query="chr1-1000", is_valid=True, chromosome="1", position=1000
        )
        SearchQueryAction.objects.create(query="legacy", is_valid=True)
        SearchQueryAction.objects.create(query="invalid", is_valid=False)
        rows = {
            row["query"]: row for row in self.client.get(self.url).json()["results"]
        }
        self.assertEqual(rows["chr1-1000"]["chromosome"], "1")
        self.assertEqual(rows["chr1-1000"]["position"], 1000)
        for query in ["legacy", "invalid"]:
            self.assertIsNone(rows[query]["chromosome"])
            self.assertIsNone(rows[query]["position"])

    def test_date_and_validity_filters(self):
        self.grant_dashboard_access()
        old = SearchQueryAction.objects.create(query="old", is_valid=False)
        SearchQueryAction.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )
        SearchQueryAction.objects.create(query="invalid today", is_valid=False)
        SearchQueryAction.objects.create(query="valid today", is_valid=True)
        today = timezone.localdate().isoformat()
        data = self.client.get(
            self.url, {"start": today, "end": today, "is_valid": "false"}
        ).json()
        self.assertEqual([row["query"] for row in data["results"]], ["invalid today"])

    def test_bad_filters_return_bad_request(self):
        self.grant_dashboard_access()
        for filters in [
            {"start": "not-a-date"},
            {"start": "2026-10-29", "end": "2026-10-28"},
            {"is_valid": "invalid"},
            {"page": "0"},
            {"page": "two"},
            {"page": "2"},
            {"page_size": "0"},
            {"page_size": "-1"},
            {"page_size": "201"},
            {"page_size": "two"},
            {"sort": "query"},
        ]:
            with self.subTest(filters=filters):
                self.assertEqual(self.client.get(self.url, filters).status_code, 400)

    def test_empty_analytics_and_dashboard_tab(self):
        self.grant_dashboard_access()
        data = self.client.get(self.url).json()
        self.assertEqual(
            data, {"results": [], "count": 0, "page": 1, "pages": 1, "page_size": 50}
        )
        response = self.client.get(reverse("tracking_dashboard"))
        self.assertContains(response, 'id="search-tab"')
        self.assertContains(response, f'data-url="{self.url}"')

    def test_tab_only_links_use_default_dashboard_filters(self):
        self.grant_dashboard_access()
        for tab in ["search", "variant", "unknown"]:
            with self.subTest(tab=tab):
                response = self.client.get(reverse("tracking_dashboard"), {"tab": tab})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].is_valid())
                self.assertContains(response, 'name="tab" id="tracking-tab"')

    def test_tab_parameter_preserves_dashboard_date_filters(self):
        self.grant_dashboard_access()
        response = self.client.get(
            reverse("tracking_dashboard"),
            {"tab": "search", "start": "2026-10-01", "end": "2026-10-31"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"]["start"].value(), "2026-10-01")
        self.assertEqual(response.context["form"]["end"].value(), "2026-10-31")

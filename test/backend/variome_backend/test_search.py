from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from variome_backend.library.models import SNV, Variant


class SnvSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="search-user")
        self.client.force_login(self.user)
        self.url = reverse("search")


        self.match = self.create_snv(
            "chr1-1000-A-G", chr="1", pos=1000, ref="A", alt="G",
            dbsnp_id="rs123", clinvar_vcv=Decimal("12345.678"),
        )
        self.nearby = self.create_snv("chr1-1005-C-T", chr="1", pos=1005)
        self.create_snv("chr1-1020-G-A", chr="1", pos=1020)
        self.create_snv("chr2-1000-A-G", chr="2", pos=1000, dbsnp_id="rs123")

        # multiple variants at the same position with different alleles
        self.create_snv("chr4-2000-T-C", chr="4", pos=2000)
        self.create_snv("chr4-2000-T-G", chr="4", pos=2000)

        self.create_snv("chr7-2000-TAA-TA", chr="7", pos=2000)

    def create_snv(self, variant_id, **snv_fields):
        variant = Variant.objects.create(variant_id=variant_id, var_type="SNV")
        return SNV.objects.create(variant=variant, type="SNV", **snv_fields)

    def test_position_search_matches_alleles_and_orders_nearby_results(self):
        response = self.client.get(
            self.url,
            {
                "resultSets": "position",
                "query": "chr1-1000-A-G",
                "chr": "1",
                "pos": "1000",
                "ref": "a",
                "alt": "g",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["term"], "chr1-1000-A-G")
        self.assertEqual(
            [item["id"] for item in body["results"]["position"]],
            [self.match.variant.id],
        )
        self.assertEqual(
            [item["snv__pos"] for item in body["results"]["nearby"][:2]],
            [1005, 1020],
        )

    def test_position_search_without_alleles_returns_nearby_results(self):
        response = self.client.get(
            self.url,
            {
                "resultSets": "position",
                "query": "chr1-1000",
                "chr": "1",
                "pos": "1000",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["term"], "chr1-1000")
        self.assertEqual(
            [item["snv__pos"] for item in body["results"]["nearby"][:2]],
            [1005, 1020],
        )
        self.assertEqual(
            [item["snv__pos"] for item in body["results"]["position"]],
            [1000],
        )
    
    def test_position_search_with_only_ref(self):
        response = self.client.get(
            self.url,
            {
                "resultSets": "position",
                "query": "chr1-1000-A",
                "chr": "1",
                "pos": "1000",
                "ref": "A",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["term"], "chr1-1000-A")
        self.assertEqual(
            [(item["snv__pos"], item["snv__chr"]) for item in body["results"]["position"]],
            [(1000, "1")],
        )

        self.assertEqual(
            [(item["snv__pos"], item["snv__chr"]) for item in body["results"]["nearby"][:2]],
            [(1005, "1"), (1020, "1")],
        )

    def test_position_search_with_multiple_variants_at_same_position(self):
        response = self.client.get(
            self.url,
            {
                "resultSets": "position",
                "query": "chr4-2000-T-C",
                "chr": "4",
                "pos": "2000",
                "ref": "T",
                "alt": "C",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["term"], "chr4-2000-T-C")
        self.assertEqual(
            sorted([(item["snv__pos"], item["snv__chr"], item["snv__ref"], item["snv__alt"]) for item in body["results"]["position"]]),
            [(2000, "4", "T", "C")],
            msg="Position search with multiple variants at the same position failed 'position' result"
        )

        self.assertEqual(
            [(item["snv__pos"], item["snv__chr"], item["snv__ref"], item["snv__alt"]) for item in body["results"]["nearby"]],
            [(2000, "4", "T", "G")],
            msg="Position search with multiple variants at the same position failed 'nearby' result"
        )








    def test_dbsnp_search_returns_matching_variants(self):
        response = self.client.get(
            self.url, {"resultSets": "dbsnp", "query": "rs123"}
        )

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]["dbsnp"]
        self.assertEqual({item["snv__chr"] for item in results}, {"1", "2"})
        self.assertTrue(all(item["snv__dbsnp_id"] == "rs123" for item in results))

    def test_clinvar_search_returns_matching_variants(self):
        response = self.client.get(
            self.url, {"resultSets": "clinvar", "query": "12345.678"}
        )

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]["clinvar"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.match.variant.id)
        self.assertEqual(results[0]["snv__clinvar_vcv"], 12345.678)

    def test_invalid_result_set_returns_bad_request(self):
        response = self.client.get(
            self.url, {"resultSets": "unsupported", "query": "value"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errors"], ["Invalid result set: unsupported"])

    def test_search_requires_authentication(self):
        self.client.logout()

        response = self.client.get(
            self.url, {"resultSets": "dbsnp", "query": "rs123"}
        )

        self.assertEqual(response.status_code, 403)

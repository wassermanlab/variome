import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TransactionTestCase
from django.urls import reverse

from variome_backend.library.models import SNV

from variome_backend.library.views import search

SEARCH_FIXTURE_VCF = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "fixtures", "vcf", "mock_snv_search.vcf"
)


def load_search_fixtures(self):
    # import_bvl_vcf manages its own transaction, so this requires TransactionTestCase
    call_command(
        "import_bvl_vcf",
        out_hyphens=False,
        out_chr=False,
        vcf_file=SEARCH_FIXTURE_VCF,
        input_tsv_dir=os.path.join("data", "fixtures"),
        progress=False,
    )


class SnvSearchResultsByID(TransactionTestCase):
    def setUp(self):
        load_search_fixtures(self)
        self.user = User.objects.create_user(username="search-user")
        self.client.force_login(self.user)
        self.url = reverse("search")
        self.match = SNV.objects.get(variant__variant_id="1_1000_A_G")

    def test_dbsnp_search_returns_matching_variants(self):
        response = self.client.get(self.url, {"resultSets": "dbsnp", "query": "rs123"})

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


class SnvSearchHttpRequests(TransactionTestCase):
    def setUp(self):
        load_search_fixtures(self)

        self.user = User.objects.create_user(username="search-user")
        self.client.force_login(self.user)
        self.url = reverse("search")

        self.match = SNV.objects.get(variant__variant_id="1_1000_A_G")

    def test_invalid_result_set_returns_bad_request(self):
        response = self.client.get(
            self.url, {"resultSets": "unsupported", "query": "value"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errors"], ["Invalid result set: unsupported"])

    def test_search_requires_authentication(self):
        self.client.logout()

        response = self.client.get(self.url, {"resultSets": "dbsnp", "query": "rs123"})

        self.assertEqual(response.status_code, 403)

    def test_position_search_http_structure(self):
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

        nearby_results = [n for n in body["results"]["nearby"]]
        nearby_results_no_id = []
        for n in nearby_results:
            n.pop("id")
            nearby_results_no_id.append(n)
        print(nearby_results_no_id)
        self.assertEqual(
            nearby_results_no_id,
            [
                {
                    "variant_id": "1_1005_C_T",
                    "var_type": "SNV",
                    "snv__pos": 1005,
                    "snv__chr": "1",
                    "snv__ref": "C",
                    "snv__alt": "T",
                    "bp_distance": 5,
                },
                {
                    "variant_id": "1_1020_G_A",
                    "var_type": "SNV",
                    "snv__pos": 1020,
                    "snv__chr": "1",
                    "snv__ref": "G",
                    "snv__alt": "A",
                    "bp_distance": 20,
                },
            ],
        )


class SnvSearchStandardResults(TransactionTestCase):
    def setUp(self):
        load_search_fixtures(self)

    def test_positional_search_chr_pos_ref_alt_no_nearby(self):

        # search using position, ref, and alt, no nearby
        (position, nearby) = search.standard_search("7", "2000", "TAA", "TA")
        position = [v["variant_id"] for v in position]
        self.assertEqual(["7_2000_TAA_TA"], position)
        self.assertEqual(len(nearby), 0)

    # only search using chromosome and position
    def test_positional_search_chr_pos(self):

        (position, nearby) = search.standard_search("7", "2000")
        position = [p["variant_id"] for p in position]
        self.assertEqual(
            position, ["7_2000_TAA_TA"], "only chromosome and position supplied"
        )

        self.assertEqual(len(nearby), 0)

    def test_positional_search_chr_pos_ref_with_nearby(self):

        # search using position, ref, expect nearby results
        (position, nearby) = search.standard_search("4", "2000", "T")
        position = [r["variant_id"] for r in position]

        self.assertEqual(position, ["4_2000_T_C", "4_2000_T_G"])

        nearby = [r["variant_id"] for r in nearby]
        self.assertEqual(nearby, ["4_2100_C_G"])

    def test_positional_search_chr_pos_ref_indel(self):

        # search using position, ref, expect nearby results
        (position, nearby) = search.standard_search("3", "50", "A")
        position = [r["variant_id"] for r in position]
        nearby = [r["variant_id"] for r in nearby]

        self.assertEqual(len(position), 2)
        self.assertTrue("3_50_AT_T" in position)
        self.assertTrue("3_50_AT_A" in position)

        self.assertEqual(len(nearby), 3)
        self.assertTrue("3_100_A_G" in nearby)
        self.assertTrue("3_100_AG_GT" in nearby)
        self.assertEqual(nearby[2], "3_101_G_T")

    def test_positional_search_chr_pos_ref_alt_multiple_same_position(self):

        (position, nearby) = search.standard_search("4", "2000", "T", "C")
        position = [p["variant_id"] for p in position]
        nearby = [n["variant_id"] for n in nearby]

        self.assertEqual(position, ["4_2000_T_C", "4_2000_T_G"])
        self.assertEqual(nearby, ["4_2100_C_G"])

    def test_positional_search_chr_pos_ref_alt_with_nearby(self):

        (position, nearby) = search.standard_search("1", "1006", "C", "G")
        position = [p["variant_id"] for p in position]
        nearby = [n["variant_id"] for n in nearby]

        self.assertEqual(len(position), 0)
        self.assertEqual(
            nearby,
            ["1_1005_C_T", "1_1000_A_G", "1_1020_G_A"],
            "nearby should be sorted by distance",
        )

    def test_positional_search_chr_pos_ref_alt_with_diff_repeat_numbers(self):

        (position, nearby) = search.standard_search("5", "100", "A", "ATGT")
        position = [p["variant_id"] for p in position]
        nearby = [n["variant_id"] for n in nearby]

        self.assertEqual(len(position), 2)
        self.assertTrue("5_100_A_ATGT" in position)
        self.assertTrue("5_100_ATGT_A" in position)

        self.assertEqual(
            nearby,
            [],
        )

    def test_positional_search_nearby_limit_10(self):
        (position, nearby) = search.standard_search("10", "207")
        (position2, nearby2) = search.standard_search("10", "208", "A", "AT")

        position = [p["variant_id"] for p in position]
        nearby = [n["variant_id"] for n in nearby]
        position2 = [p["variant_id"] for p in position2]
        nearby2 = [n["variant_id"] for n in nearby2]

        self.assertEqual(len(nearby), 10)
        self.assertEqual(len(nearby2), 10)
        self.assertEqual(position, ["10_207_A_AT"])
        self.assertEqual(
            nearby,
            [
                "10_206_A_AT",
                "10_205_A_AT",
                "10_209_A_AT",
                "10_204_A_AT",
                "10_210_A_AT",
                "10_203_A_AT",
                "10_211_A_AT",
                "10_202_A_AT",
                "10_212_A_AT",
                "10_201_A_AT",
            ],
        )
        self.assertEqual(position2, [])
        self.assertEqual(
            nearby2,
            [
                "10_207_A_AT",
                "10_209_A_AT",
                "10_206_A_AT",
                "10_210_A_AT",
                "10_205_A_AT",
                "10_211_A_AT",
                "10_204_A_AT",
                "10_212_A_AT",
                "10_203_A_AT",
                "10_213_A_AT",
            ],
        )

        (position3, nearby3) = search.standard_search("10", "220")
        position3 = [v["variant_id"] for v in position3]
        nearby3 = [v["variant_id"] for v in nearby3]
        self.assertEqual(
            position3,
            [
                "10_220_A_AT",
                "10_220_A_ATAT",
                "10_220_A_ATATAT",
                "10_220_A_ATATATAT",
                "10_220_A_ATATATATAT",
            ],
        )
        self.assertEqual(
            nearby3,
            [
                "10_214_A_AT",
                "10_213_A_AT",
                "10_212_A_AT",
                "10_211_A_AT",
                "10_210_A_AT",
                "10_209_A_AT",
                "10_207_A_AT",
                "10_206_A_AT",
                "10_205_A_AT",
                "10_204_A_AT",
            ],
        )


#        self.assertEqual(position, [])
class SnvSearchValidation(TransactionTestCase):
    def test_standard_validation(self):

        self.assertEqual(
            search.standard_validate(chr="90", pos="1", ref="A", alt="T"),
            "Invalid chromosome: 90",
        )
        self.assertEqual(
            search.standard_validate(chr="23", pos="1", ref="A", alt="T"),
            "Invalid chromosome: 23",
        )
        self.assertEqual(
            search.standard_validate(chr="bad", pos="1", ref="A", alt="T"),
            "Invalid chromosome: bad",
        )
        self.assertEqual(
            search.standard_validate(chr=None, pos="1", ref="A", alt="T"),
            "Chromosome is null",
        )
        self.assertEqual(
            search.standard_validate(chr="1", pos="1a", ref="A", alt="T"),
            "Invalid position (must be numeric): 1a",
        )
        self.assertEqual(
            search.standard_validate(chr="1", pos="-2", ref="A", alt="T"),
            "Invalid position: -2",
        )

from decimal import Decimal
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from variome_backend.library.models import (
    MT,
    SNV,
    Gene,
    GenomicGnomadFrequency,
    GenomicVariomeFrequency,
    MtGnomadFrequency,
    MtVariomeFrequency,
    Transcript,
    Variant,
    VariantAnnotation,
    VariantTranscript,
)
from variome_backend.library.views.search import standard_search, standard_validate
from variome_backend.library_access.models import UserProfile
from variome_backend.models import VariomeSettings


class MitochondrialBackendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="mt-user")
        UserProfile.objects.update_or_create(
            user=cls.user, defaults={"accesses_per_day": 100}
        )
        cls.variant = Variant.objects.create(variant_id="M_1000_A_G", var_type="M")
        cls.mt = MT.objects.create(
            variant=cls.variant,
            pos=1000,
            ref="A",
            alt="G",
            dbsnp_id="rs123",
            clinvar_vcv=Decimal("12345.678"),
            mitomap_url="https://www.mitomap.org/",
        )
        for pos, ref, alt in ((1000, "A", "T"), (1005, "C", "T"), (1020, "G", "A")):
            variant = Variant.objects.create(
                variant_id=f"M_{pos}_{ref}_{alt}", var_type="M"
            )
            MT.objects.create(variant=variant, pos=pos, ref=ref, alt=alt)
        outside = Variant.objects.create(variant_id="M_1500_A_G", var_type="M")
        MT.objects.create(variant=outside, pos=1500, ref="A", alt="G")
        cls.snv_variant = Variant.objects.create(
            variant_id="1_1000_A_G", var_type="SNV"
        )
        SNV.objects.create(
            variant=cls.snv_variant,
            type="SNV",
            chr="1",
            pos=1000,
            ref="A",
            alt="G",
            dbsnp_id="rs123",
            clinvar_vcv=Decimal("12345.678"),
        )
        MtVariomeFrequency.objects.create(
            variant=cls.variant,
            an=100,
            ac_hom=2,
            ac_het=3,
            af_hom=Decimal("0.02"),
            af_het=Decimal("0.03"),
            max_hl=Decimal("0.9"),
            hl_hist="1,2,3,4,5,6,7,8,9,10",
        )
        MtGnomadFrequency.objects.create(variant=cls.variant, an=200, ac_het=4)
        GenomicVariomeFrequency.objects.create(variant=cls.snv_variant, an_tot=80)
        GenomicGnomadFrequency.objects.create(variant=cls.snv_variant, an_tot=160)
        gene = Gene.objects.create(short_name="MT-ND1")
        transcript = Transcript.objects.create(
            transcript_id="ENST_MT", transcript_type="E", gene=gene
        )
        variant_transcript = VariantTranscript.objects.create(
            variant=cls.variant, transcript=transcript, hgvsc="m.1000A>G"
        )
        VariantAnnotation.objects.create(
            variant_transcript=variant_transcript, impact="MODERATE"
        )
        VariomeSettings.objects.update_or_create(
            pk=1,
            defaults={
                "home_page_message": "Welcome",
                "example_snv": cls.snv_variant,
                "example_mt": cls.variant,
            },
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_chromosome_aliases_exact_ref_alt_and_nearby(self):
        for chromosome in ("M", "MT", "chrM", "chrMT", "chrmt"):
            with self.subTest(chromosome=chromosome):
                self.assertIsNone(standard_validate(chromosome, "1000"))
                response = self.client.get(
                    reverse("search"),
                    {
                        "resultSets": "position",
                        "query": f"{chromosome}-1000-A-G",
                        "chr": chromosome,
                        "pos": "1000",
                        "ref": "a",
                        "alt": "g",
                    },
                )
                self.assertEqual(response.status_code, 200)
                results = response.json()["results"]
                self.assertEqual(
                    [item["variant_id"] for item in results["position"]],
                    ["M_1000_A_G", "M_1000_A_T"],
                )
                self.assertEqual(
                    [item["variant_id"] for item in results["nearby"]],
                    ["M_1005_C_T", "M_1020_G_A"],
                )
                exact = results["position"][0]
                self.assertEqual(exact["var_type"], "M")
                self.assertEqual(
                    {
                        key: exact[key]
                        for key in ("snv__chr", "snv__pos", "snv__ref", "snv__alt")
                    },
                    {
                        "snv__chr": "M",
                        "snv__pos": 1000,
                        "snv__ref": "A",
                        "snv__alt": "G",
                    },
                )
                self.assertEqual(results["nearby"][0]["bp_distance"], 5)

    def test_exact_ref_alt_match_precedes_other_alleles(self):
        position, _ = standard_search("MT", 1000, "A", "T")
        self.assertEqual(position[0]["variant_id"], "M_1000_A_T")

    def test_positional_search_does_not_mix_nuclear_and_mt_variants(self):
        position, nearby = standard_search("1", 1000)
        self.assertEqual([item["id"] for item in position], [self.snv_variant.id])
        self.assertEqual(nearby, [])

    def test_dbsnp_search_includes_both_models(self):
        response = self.client.get(
            reverse("search"), {"resultSets": "dbsnp", "query": "rs123"}
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]["dbsnp"]
        self.assertEqual(
            {item["id"] for item in results}, {self.variant.id, self.snv_variant.id}
        )
        self.assertEqual({item["snv__chr"] for item in results}, {"1", "M"})
        self.assertTrue(all(item["snv__dbsnp_id"] == "rs123" for item in results))

    def test_clinvar_search_accepts_numeric_and_vcv_identifiers(self):
        for query in ("12345.678", "VCV000012345.678", "vcv000012345.678"):
            with self.subTest(query=query):
                response = self.client.get(
                    reverse("search"), {"resultSets": "clinvar", "query": query}
                )
                self.assertEqual(response.status_code, 200)
                results = response.json()["results"]["clinvar"]
                self.assertEqual(
                    {item["id"] for item in results},
                    {self.variant.id, self.snv_variant.id},
                )
                self.assertTrue(
                    all(item["snv__clinvar_vcv"] == 12345.678 for item in results)
                )

    def test_invalid_clinvar_and_missing_result_set_are_bad_requests(self):
        for parameters in (
            {"query": "rs123"},
            {"resultSets": "clinvar", "query": "VCVbad"},
            {"resultSets": "clinvar", "query": "NaN"},
        ):
            with self.subTest(parameters=parameters):
                self.assertEqual(
                    self.client.get(reverse("search"), parameters).status_code, 400
                )

    def test_mt_detail_includes_frequencies_and_shared_annotations(self):
        response = self.client.get(reverse("variant", args=[self.variant.id]))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["variant"]["var_type"], "M")
        self.assertIsNone(body["snv"])
        self.assertEqual(body["mt"]["variant"]["id"], self.variant.id)
        self.assertEqual(body["mt"]["pos"], 1000)
        self.assertEqual(body["mt"]["mitomap_url"], "https://www.mitomap.org/")
        self.assertEqual(Decimal(body["mt"]["clinvar_vcv"]), Decimal("12345.678"))
        self.assertEqual(body["bvlFrequencies"]["an"], 100)
        self.assertEqual(body["bvlFrequencies"]["hl_hist"], "1,2,3,4,5,6,7,8,9,10")
        self.assertEqual(Decimal(body["bvlFrequencies"]["max_hl"]), Decimal("0.9"))
        self.assertEqual(body["gnomadFrequencies"]["an"], 200)
        self.assertIsNone(body["gnomadFrequencies"]["af_hom"])
        self.assertEqual(body["annotations"][0]["gene"], "MT-ND1")
        self.assertEqual(body["annotations"][0]["transcripts"][0]["impact"], "MODERATE")
        self.assertEqual(body["errors"], [[]])

    def test_snv_detail_keeps_genomic_serializers(self):
        response = self.client.get(reverse("variant", args=[self.snv_variant.id]))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNone(body["mt"])
        self.assertEqual(body["snv"]["chr"], "1")
        self.assertEqual(body["bvlFrequencies"]["an_tot"], 80)
        self.assertEqual(body["gnomadFrequencies"]["an_tot"], 160)

    def test_mt_detail_handles_missing_frequencies(self):
        MtVariomeFrequency.objects.filter(variant=self.variant).delete()
        MtGnomadFrequency.objects.filter(variant=self.variant).delete()
        response = self.client.get(reverse("variant", args=[self.variant.id]))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNotNone(body["mt"])
        self.assertIsNone(body["bvlFrequencies"])
        self.assertIsNone(body["gnomadFrequencies"])
        self.assertIn(
            "mitochondrial gnomad frequency not found for this variant", body["errors"]
        )

    def test_search_and_detail_require_authentication(self):
        self.client.logout()
        for url in (reverse("search"), reverse("variant", args=[self.variant.id])):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_mt_detail_preserves_access_count_gate(self):
        with (
            patch.object(
                UserProfile,
                "access_count",
                new_callable=PropertyMock,
                return_value=101,
            ),
            patch(
                "variome_backend.library_access.decorators.notify_access_limit_reached"
            ) as notify,
        ):
            self.assertEqual(
                self.client.get(reverse("variant", args=[self.variant.id])).status_code,
                429,
            )
            notify.assert_called_once()

    def test_settings_expose_examples_only_when_authenticated(self):
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        settings = response.json()["settings"]
        self.assertEqual(
            settings["example_mt"], {"id": self.variant.id, "var_id": "M_1000_A_G"}
        )
        self.assertEqual(settings["example_snv"]["id"], self.snv_variant.id)
        self.client.logout()
        settings = self.client.get(reverse("settings")).json()["settings"]
        self.assertEqual(settings["home_page_message"], "Welcome")
        self.assertIsNone(settings["example_mt"])
        self.assertIsNone(settings["example_snv"])

    def test_settings_clear_deleted_mitochondrial_example(self):
        self.variant.delete()
        settings = self.client.get(reverse("settings")).json()["settings"]
        self.assertIsNone(settings["example_mt"])
        self.assertEqual(settings["example_snv"]["id"], self.snv_variant.id)

    def test_models_allow_missing_numeric_values_and_blank_links(self):
        variant = Variant.objects.create(variant_id="M_2000_A_G", var_type="M")
        frequency = MtVariomeFrequency.objects.create(variant=variant)
        self.assertIsNone(frequency.an)
        self.assertIsNone(frequency.max_hl)
        self.assertEqual(frequency.hl_hist, "")
        self.assertEqual(self.mt.dbsnp_url, "")
        self.assertEqual(self.variant.mt, self.mt)

    def test_mt_record_is_unique_per_variant(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MT.objects.create(variant=self.variant, pos=1000, ref="A", alt="T")

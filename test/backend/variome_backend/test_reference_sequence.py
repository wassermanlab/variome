import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from pyfaidx import Fasta
from rest_framework.test import APIClient

FASTA = b">1 dna:chromosome chromosome:GRCh38:1:1:12:1\nACGTac\nGTNNAA\n>MT\nGATTACA\n"


class ReferenceSequenceTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.reference = Path(self.directory.name) / "GRCh38.fa"
        self.reference.write_bytes(FASTA)
        with Fasta(str(self.reference)):
            pass
        self.settings_override = self.settings(
            REFERENCE_GENOME_PATH=str(self.reference)
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.client = APIClient()
        self.client.force_authenticate(
            User.objects.create_user(username="reference-user")
        )

    def lookup(self, region="1:1..1:1", **query):
        return self.client.get(
            reverse("reference_sequence", args=[region]), query
        )

    def test_route_has_no_species_segment(self):
        self.assertEqual(
            reverse("reference_sequence", args=["1:1..1:1"]),
            "/api/sequence/region/1:1..1:1",
        )
        self.assertEqual(
            self.client.get("/api/sequence/region/human/1:1..1:1").status_code,
            404,
        )

    def test_inclusive_coordinates_and_uppercase(self):
        for region, expected in [
            ("1:1..1:1", "A"),
            ("1:5..8:1", "ACGT"),
            ("1:12..12:1", "A"),
            ("1:2..5:-1", "TACG"),
            ("1:1..2", "AC"),
            ("chr1:1..2:1", "AC"),
        ]:
            with self.subTest(region=region):
                response = self.lookup(
                    region,
                    coord_system_version="GRCh38",
                    **{"content-type": "application/json"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"seq": expected})

    def test_mitochondrial_aliases(self):
        for chromosome in ["M", "MT", "chrM", "chrMT"]:
            with self.subTest(chromosome=chromosome):
                response = self.lookup(f"{chromosome}:1..3:1")
                self.assertEqual(response.json(), {"seq": "GAT"})

    def test_sequence_length_limit(self):
        reference = self.reference.parent / "length.fa"
        reference.write_text(">1\n" + "A" * 202 + "\n")
        with Fasta(str(reference)):
            pass
        with self.settings(REFERENCE_GENOME_PATH=str(reference)):
            response = self.lookup("1:2..201:1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"seq": "A" * 200})

            response = self.lookup("1:2..202:1")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json(),
                {"error": "Invalid region or region exceeds 200 bases."},
            )

    def test_invalid_regions(self):
        for region in [
            "1:0..1:1",
            "1:5..4:1",
            "1:1..13:1",
            "unknown:1..1:1",
            "1:1..10000001:1",
            "1:1..2:0",
            "1:one..two:1",
            "1:1",
            f"1:{'1' * 100}..2:1",
            f"{'-' * 1000}:1..2:1",
        ]:
            with self.subTest(region=region):
                self.assertEqual(self.lookup(region).status_code, 400)

    def test_unsupported_assembly(self):
        self.assertEqual(self.lookup(coord_system_version="GRCh37").status_code, 400)

    def test_missing_reference_returns_service_unavailable(self):
        self.reference.unlink()
        response = self.lookup()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(str(self.reference), response.content.decode())

    def test_missing_index_is_not_built_during_request(self):
        index = Path(f"{self.reference}.fai")
        index.unlink()
        self.assertEqual(self.lookup().status_code, 503)
        self.assertFalse(index.exists())

    def test_reference_and_index_are_not_modified(self):
        index = Path(f"{self.reference}.fai")
        before = (self.reference.stat().st_mtime_ns, index.stat().st_mtime_ns)
        self.assertEqual(self.lookup().status_code, 200)
        self.assertEqual(
            before, (self.reference.stat().st_mtime_ns, index.stat().st_mtime_ns)
        )

    def test_authentication_and_http_method(self):
        self.assertEqual(
            self.client.post(
                reverse("reference_sequence", args=["1:1..1:1"])
            ).status_code,
            405,
        )
        self.client.force_authenticate(user=None)
        self.assertEqual(self.lookup().status_code, 403)

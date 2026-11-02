import errno
import gzip
import io
import tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from pyfaidx import Fasta
from rest_framework.test import APIClient

from variome_backend.management.commands.download_reference_genome import (
    Command,
    REFERENCE_URL,
)


FASTA = b">1 dna:chromosome chromosome:GRCh38:1:1:12:1\nACGTac\nGTNNAA\n>MT\nGATTACA\n"
COMMAND_MODULE = "variome_backend.management.commands.download_reference_genome"


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


class DownloadReferenceGenomeTests(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.reference = self.root / "configured" / "GRCh38.fa"
        self.settings_override = self.settings(
            REFERENCE_GENOME_PATH=str(self.reference), BASE_DIR=self.root
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.output = io.StringIO()
        self.download = patch(
            f"{COMMAND_MODULE}.urlopen",
            return_value=io.BytesIO(gzip.compress(FASTA)),
        ).start()
        self.addCleanup(patch.stopall)

    def run_command(self):
        call_command("download_reference_genome", stdout=self.output)

    def test_download_decompresses_and_indexes(self):
        self.run_command()
        self.download.assert_called_once_with(REFERENCE_URL, timeout=60)
        self.assertEqual(self.reference.read_bytes(), FASTA)
        with Fasta(str(self.reference), build_index=False, rebuild=False) as genome:
            self.assertEqual(str(genome["1"][4:8]), "acGT")
        self.assertIn("Reference and index ready", self.output.getvalue())
        self.assertEqual(
            {path.name for path in self.reference.parent.iterdir()},
            {"GRCh38.fa", "GRCh38.fa.fai"},
        )

    def test_unwritable_location_falls_back_to_repository_root(self):
        create_temporary = Command.create_temporary

        def create(command, destination):
            if destination == self.reference:
                raise PermissionError(errno.EACCES, "Permission denied")
            return create_temporary(command, destination)

        with patch.object(Command, "create_temporary", create):
            self.run_command()
        fallback = self.root / "GRCh38.fa"
        self.assertEqual(fallback.read_bytes(), FASTA)
        self.assertTrue(Path(f"{fallback}.fai").exists())
        self.assertFalse(self.reference.exists())
        message = self.output.getvalue()
        self.assertIn("Move", message)
        self.assertIn(str(self.reference), message)
        self.assertIn(f"{fallback}.fai", message)

    def test_existing_reference_is_not_overwritten(self):
        self.reference.parent.mkdir()
        self.reference.write_text("existing reference")
        with self.assertRaisesMessage(CommandError, "already exists"):
            self.run_command()
        self.download.assert_not_called()
        self.assertEqual(self.reference.read_text(), "existing reference")

    def test_download_failure_cleans_up(self):
        self.download.side_effect = URLError("Connection unavailable")
        with self.assertRaisesMessage(CommandError, "download or indexing failed"):
            self.run_command()
        self.assertEqual(list(self.reference.parent.iterdir()), [])

    def test_invalid_download_cleans_up(self):
        for content in [
            b"not gzip",
            gzip.compress(b"not FASTA"),
            gzip.compress(b">1\nACGT\n"),
        ]:
            with self.subTest(content=content):
                self.download.return_value = io.BytesIO(content)
                with self.assertRaises(CommandError):
                    self.run_command()
                self.assertEqual(list(self.reference.parent.iterdir()), [])

    def test_disk_full_does_not_fall_back(self):
        with patch.object(
            Command, "create_temporary", side_effect=OSError(errno.ENOSPC, "Disk full")
        ):
            with self.assertRaisesMessage(CommandError, "Cannot prepare"):
                self.run_command()
        self.download.assert_not_called()

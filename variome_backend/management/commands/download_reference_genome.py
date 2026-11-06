import errno
import gzip
import shutil
import tempfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pyfaidx import Fasta, FastaIndexingError

REFERENCE_URL = (
    "https://ftp.ensembl.org/pub/release-115/fasta/homo_sapiens/dna/"
    "Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz"
)


class Command(BaseCommand):
    help = "Download and index the human GRCh38 reference at REFERENCE_GENOME_PATH."

    def handle(self, *args, **options):
        configured_path = Path(settings.REFERENCE_GENOME_PATH).expanduser()
        destination = configured_path
        try:
            temporary = self.create_temporary(destination)
        except OSError as exc:
            if exc.errno not in (errno.EACCES, errno.EPERM, errno.EROFS):
                raise CommandError(
                    f"Cannot prepare reference destination: {exc}"
                ) from exc
            destination = Path(settings.BASE_DIR) / configured_path.name
            try:
                temporary = self.create_temporary(destination)
            except OSError as fallback_exc:
                raise CommandError(
                    f"Cannot write to repository root: {fallback_exc}"
                ) from fallback_exc

        temporary_path = Path(temporary.name)
        temporary_index = Path(f"{temporary_path}.fai")
        try:
            self.stdout.write(f"Downloading GRCh38 from {REFERENCE_URL}")
            with temporary, urlopen(REFERENCE_URL, timeout=60) as response:
                with gzip.GzipFile(fileobj=response) as genome:
                    shutil.copyfileobj(genome, temporary, length=1024 * 1024)
            with Fasta(str(temporary_path)) as genome:
                if "1" not in genome or "MT" not in genome:
                    raise CommandError("Downloaded FASTA lacks GRCh38 chromosomes.")
            temporary_path.replace(destination)
            temporary_index.replace(Path(f"{destination}.fai"))
        except (OSError, EOFError, URLError, FastaIndexingError) as exc:
            raise CommandError(f"Reference download or indexing failed: {exc}") from exc
        finally:
            temporary.close()
            temporary_path.unlink(missing_ok=True)
            temporary_index.unlink(missing_ok=True)

        self.stdout.write(
            self.style.SUCCESS(f"Reference and index ready: {destination}")
        )
        if destination != configured_path:
            self.stdout.write(
                self.style.WARNING(
                    f"Configured location is unwritable. Move {destination} and "
                    f"{destination}.fai to {configured_path} and "
                    f"{configured_path}.fai, and make both readable by Django."
                )
            )

    def create_temporary(self, destination):
        if Path(f"{destination}.fai").exists():
            raise CommandError(f"Reference or index already exists at {destination}.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        return tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{destination.name}.",
            suffix=".fa",
            dir=destination.parent,
            delete=False,
        )

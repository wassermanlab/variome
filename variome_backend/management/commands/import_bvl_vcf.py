import argparse
import hashlib
import json
import logging
import pprint
import sys
import warnings as pywarnings
from contextlib import contextmanager
from pathlib import Path
from time import time

from django.core.management.base import BaseCommand
from django.db import transaction

import variome_backend.management.import_tools as bvltools
from variome_backend.management.vcf_import_settings import VcfImportSettings
from variome_backend.management.VCFCallFilters.GenesCallFilter import GenesCallFilter
from variome_backend.management.VCFCallFilters.TranscriptsCallFilter import TranscriptsCallFilter
from variome_backend.management.VCFCallFilters.VariantsCallFilter import VariantsCallFilter
from variome_backend.management.VCFCallFilters.VariantsTranscriptsCallFilter import VariantsTranscriptsCallFilter
from variome_backend.management.VCFCallFilters.VariantsAnnotationsCallFilter import VariantsAnnotationsCallFilter
from variome_backend.management.VCFCallFilters.VariantsConsequencesCallFilter import VariantsConsequencesCallFilter
from variome_backend.management.VCFCallFilters.SnvsCallFilter import SnvsCallFilter
from variome_backend.management.VCFCallFilters.GenomicBvlFrequenciesCallFilter import GenomicBvlFrequenciesCallFilter
from variome_backend.management.VCFCallFilters.MtsCallFilter import MtsCallFilter
from variome_backend.management.VCFCallFilters.MtBvlFrequenciesCallFilter import MtBvlFrequenciesCallFilter
from variome_backend.management.VCFCallFilters.MtGnomadFrequenciesCallFilter import MtGnomadFrequenciesCallFilter

log = logging.getLogger("management")

DEFAULT_VERBOSITY = 2
MAX_VERBOSITY = 3

HELP_EPILOG = """\
verbosity:
  -v     summary only: the final Import summary and duration; logging,
         warnings, error/warning listings and progress are suppressed
  -vv    (default) normal output: logging, error/warning listings and
         progress, without chromosome caching messages or step timings
  -vvv   everything, including "Caching chromosome ..." messages and
         per-table / per-1000-row timings

import summary:
  Counts are for this run, not whole-table database totals.
    Processed  input rows read for the table
    Created    new rows inserted (bulk creates count only after the insert
               succeeds)
    Updated    existing rows updated; includes rows whose values were
               already identical (not a count of changed fields)
    Skipped    ignored existing rows, rejected rows, or pending inserts
               abandoned on an early stop
    Failed     rows that failed to import
    Deleted    existing rows deleted by --delete (excludes cascaded
               deletions of related tables)
  Each row is marked \u2705 when the table imported without failures and \u274c
  when it had failed rows or import errors (or the whole table failed and
  was rolled back). Dry-run and rollback summaries are labelled as not
  committed. Duration is the wall-clock time of the whole command.
"""


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


@contextmanager
def quiet_output():
    """Silence logging and Python warnings (used for -v)."""
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with pywarnings.catch_warnings():
            pywarnings.simplefilter("ignore")
            yield
    finally:
        logging.disable(previous)


def check_vcf(vcf_path, settings):
    """Check a VCF file (gzipped or plain) for read errors. Logs warnings on failure."""
    log.info("Checking VCF file: %s", vcf_path)
    n = 0
    last_record = None
    try:
        call_filter = VariantsCallFilter(vcf_path, settings)
        info_fields = " ".join(call_filter.vcf_header.info_ids())
        log.info("VCF INFO fields:\n%s", info_fields)
        log.info("VCF CSQ fields:\n%s", " ".join(call_filter.csq_fields))
        for record in call_filter.vcf_record_stream():
            n += 1
            last_record = record
    except Exception as e:
        log.warning("Error reading VCF file %s: %s", vcf_path, e)
        if last_record is not None:
            log.warning("Last successful record was number %d: %s", n, last_record)
            log.warning(
                "The VCF file will continue to be processed, but this may indicate "
                "a problem that could lead to incomplete or incorrect results."
            )
        else:
            log.warning("No records were successfully read from the VCF file.")
            sys.exit(1)


def _write_to_tsv(row_iter, table_name, output_dir, batch_size=10000):
    """Consume row_iter and write all rows to a TSV file. Does not import into the database."""
    output_path = Path(output_dir) / f"{table_name}.tsv"
    header = None
    batch = []
    with open(output_path, "w", encoding="utf-8") as f:
        for row in row_iter:
            if header is None:
                header = list(row.keys())
                f.write("\t".join(header) + "\n")
            batch.append("\t".join(str(row.get(col, "")) for col in header) + "\n")
            if len(batch) >= batch_size:
                f.writelines(batch)
                batch = []
        if batch:
            f.writelines(batch)
    log.info("TSV written: %s", output_path)


def compute_dir_hash(dir_path):
    """Compute per-file SHA-256 hashes for all TSV files in a directory.

    Returns (hash_list_json, hash_map, final_hash).
    """
    def file_hash(path):
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    hash_map = {}
    for file in sorted(Path(dir_path).glob("*.tsv")):
        hash_map[file.name] = file_hash(file)

    final_hasher = hashlib.sha256()
    hash_list_json = json.dumps(hash_map, indent=2)
    final_hasher.update(hash_list_json.encode('utf-8'))
    return hash_list_json, hash_map, final_hasher.hexdigest()


class Command(BaseCommand):
    help = "Import bvl data directly from a VCF file"

    def log_errors(self, entity_type, errors):
        if errors and self.verbosity >= 2:
            sys.stderr.write(f"\nERRORS ({len(errors)}) in {entity_type} load:\n")
            for line in bvltools.format_errors(errors, log_all=self.log_all_errors):
                sys.stderr.write(line + "\n")

    def log_warnings(self, entity_type, warnings):
        if warnings and self.verbosity >= 2:
            sys.stderr.write(f"\nWARNINGS ({len(warnings)}) in {entity_type} load:\n")
            for line in bvltools.format_messages(warnings, log_all=self.log_all_errors):
                sys.stderr.write(line + "\n")

    def add_arguments(self, parser):
        parser.formatter_class = HelpFormatter
        parser.epilog = HELP_EPILOG

        # Replace Django's "-v {0,1,2,3}" with a counted -v / -vv / -vvv flag
        for action in list(parser._actions):
            if action.dest == "verbosity":
                parser._handle_conflict_resolve(
                    None, [(opt, action) for opt in action.option_strings]
                )
        parser.add_argument(
            "-v",
            action="count",
            dest="verbosity",
            default=argparse.SUPPRESS,
            help="Output verbosity: -v summary only, -vv normal (default), "
            "-vvv adds chromosome caching messages and timings",
        )
        parser.add_argument(
            "--verbosity",
            type=int,
            choices=[1, 2, 3],
            dest="verbosity",
            default=argparse.SUPPRESS,
            help="Same as -v/-vv/-vvv (default: 2)",
        )

        # --- VCF source ---
        parser.add_argument(
            "--vcf",
            dest="vcf_file",
            default="data/fixtures/vcf/variome-tiny.vcf",
            help="Path to input VCF file (plain or gzipped)",
        )

        # --- VCF interpretation settings ---
        parser.add_argument(
            "--na",
            default=".",
            help="Value used to represent missing/null data",
        )
        parser.add_argument(
            "--out-chr",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Prefix chromosome names with 'chr' - does not use a prefix when false",
        )
        parser.add_argument(
            "--out-hyphens",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Use hyphens in variant IDs (e.g. 1-100-A-G); uses underscores when false",
        )
        parser.add_argument(
            "--default-transcript-source",
            default="E",
            dest="default_transcript_source",
            help="Default transcript source when unknown (E=Ensembl, R=RefSeq)",
        )
        parser.add_argument(
            "--cadd-threshold",
            type=int,
            default=20,
            dest="cadd_threshold",
            help="CADD phred score threshold for 'Damaging' classification",
        )
        parser.add_argument(
            "--input-tsv-dir", # still needed for severities, which are not read from the VCF
            default="data/fixtures",
            dest="input_tsv_dir",
            help="Path to the dir of the severities TSV file used by VCF filters",
        )
        parser.add_argument(
            "--ranges",
            default=None,
            help=(
                "Comma-separated chromosome ranges to restrict processing, "
                "e.g. '22:27010000-27020000,X:2702000-2802000'"
            ),
        )

        # --- TSV conversion / hash comparison ---
        parser.add_argument(
            "--convert-to-tsv",
            default=False,
            action=argparse.BooleanOptionalAction,
            dest="convert_to_tsv",
            help="Write TSV files instead of importing into the database",
        )
        parser.add_argument(
            "--tsv-output-dir",
            default="data/vcf_output",
            dest="tsv_output_dir",
            help="Directory to write TSV files when --convert-to-tsv is used",
        )
        parser.add_argument(
            "--hash-compare",
            default=None,
            dest="hash_compare",
            help=(
                "Directory of an existing TSV set to compare hashes against. "
                "Requires --convert-to-tsv."
            ),
        )

        parser.add_argument(
            "--dedupe-cache-window",
            "-c",
            type=int,
            default=10000,
            help="The size of the window to use when preloading variant position ranges to check existing data when --delete is not used"
        )

        # --- Table selection (mirrors import_bvl) ---
        parser.add_argument("--severities", default=True, action=argparse.BooleanOptionalAction,
                            help="Process severity table?")
        parser.add_argument("--genes", default=True, action=argparse.BooleanOptionalAction,
                            help="Process genes?")
        parser.add_argument("--variants", default=True, action=argparse.BooleanOptionalAction,
                            help="Process variants?")
        parser.add_argument("--transcripts", default=True, action=argparse.BooleanOptionalAction,
                            help="Process transcripts?")
        parser.add_argument("--snvs", default=True, action=argparse.BooleanOptionalAction,
                            help="Process SNVs?")
        parser.add_argument("--gvfs", default=True, action=argparse.BooleanOptionalAction,
                            help="Process genomic variome frequencies?")
        parser.add_argument("--mts", default=True, action=argparse.BooleanOptionalAction,
                            help="Process mitochondrial metadata and cohort frequencies?")
        parser.add_argument("--mt-gnomad-tsv", default=None,
                            help="Optional gnomAD mitochondrial frequency TSV to intersect with the VCF")
        parser.add_argument("--annotations", default=True, action=argparse.BooleanOptionalAction,
                            help="Process variant annotations?")
        parser.add_argument("--consequences", default=True, action=argparse.BooleanOptionalAction,
                            help="Process variant consequences?")
        parser.add_argument("--vts", default=True, action=argparse.BooleanOptionalAction,
                            help="Process variant transcripts?")

        # --- Shared DB/run flags (mirrors import_bvl) ---
        parser.add_argument(
            "--progress",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Show progress indications?",
        )
        parser.add_argument(
            "--failfast", "-f",
            default=False,
            action=argparse.BooleanOptionalAction,
            help="Fail on first error?",
        )
        parser.add_argument(
            "--batch",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Batch database updates to improve performance",
        )
        parser.add_argument(
            "--batchsize",
            type=int,
            default=999,
            help= "Batch size for bulk creates - 999 is limit for SQLite, larger numbers may make things faster with PostgreSQL"
        )
        parser.add_argument(
            "--delete",
            default=False,
            action=argparse.BooleanOptionalAction,
            help="Delete existing data before importing",
        )
        parser.add_argument(
            "--ignore-existing", "-i",
            dest="ignore-existing",
            action="store_true",
            default=False,
            help="Ignore input rows that already exist in the database",
        )
        parser.add_argument(
            "--rollback-on-error", "-r",
            dest="rollback-on-error",
            action="store_true",
            default=False,
            help="Roll back all database changes if any errors occur",
        )
        parser.add_argument(
            "--dry-run", "-n",
            dest="dry-run",
            action="store_true",
            default=False,
            help="Dry run - make no changes to the database",
        )
        parser.add_argument(
            "--log-all-errors",
            dest="log_all_errors",
            action="store_true",
            default=False,
            help="Print every error in full; by default only the first 10 per error group are shown",
        )

    def handle(self, **options):
        verbosity = options.get("verbosity") or DEFAULT_VERBOSITY
        self.verbosity = max(1, min(verbosity, MAX_VERBOSITY))
        options["verbosity"] = self.verbosity
        if self.verbosity == 1:
            with quiet_output():
                return self._handle(**options)
        return self._handle(**options)

    @transaction.atomic
    def _handle(self, **options):
        log.debug("import_bvl_vcf got options:\n%s", pprint.pformat(options))
        start_time = time()
        self.log_all_errors = options["log_all_errors"]

        vcf_file = options["vcf_file"]
        settings = VcfImportSettings(
            VCF_FILE=vcf_file,
            NA=options["na"],
            OUT_CHR=options["out_chr"],
            OUT_HYPHENS=options["out_hyphens"],
            DEFAULT_TRANSCRIPT_SOURCE=options["default_transcript_source"],
            CADD_DAMAGING_THRESHOLD=options["cadd_threshold"],
            INPUT_TSV_PATH=options["input_tsv_dir"],
            HASH_COMPARE=options["hash_compare"],
            RANGES=options["ranges"],
        )

        convert_to_tsv = options["convert_to_tsv"]

        check_vcf(vcf_file, settings)

        # Helper that returns a row generator for the given filter class
        def make_row_iter(filter_cls, **filter_kwargs):
            if filter_cls is MtGnomadFrequenciesCallFilter:
                filter_kwargs["tsv_path"] = options["mt_gnomad_tsv"]
            return filter_cls(vcf_file, settings, **filter_kwargs).getTableRows()

        if not options["delete"]:
            first_existing_variant = bvltools.VariantImporter.model.objects.first()
            if self.verbosity >= 3:
                self.stderr.write(f"First existing variant: {first_existing_variant}")
            check_fail_reason = False
            if first_existing_variant is not None:
                if "-" in first_existing_variant.variant_id and not options["out_hyphens"]:
                    check_fail_reason = "-"
                if "_" in first_existing_variant.variant_id and options["out_hyphens"]:
                    check_fail_reason = "_"
                if "chr" in first_existing_variant.variant_id and not options["out_chr"]:
                    check_fail_reason = "chr prefix"
                if "chr" not in first_existing_variant.variant_id and options["out_chr"]:
                    check_fail_reason = "no chr prefix"
            if check_fail_reason:
                log.error(f"inconsistent variant_id format was detected: Existing data uses {check_fail_reason}. Please adjust --out-hyphens or --out-chr flags to make consistent with your first variant's ID, which is {first_existing_variant.variant_id}")
                exit()
        # Table selection flags and corresponding filter / importer pairs
        table_specs = []
        if options["genes"]:
            table_specs.append(("Gene", "genes", GenesCallFilter, bvltools.GeneImporter))
        if options["variants"]:
            table_specs.append(("Variant", "variants", VariantsCallFilter, bvltools.VariantImporter))
        if options["transcripts"]:
            table_specs.append(("Transcript", "transcripts", TranscriptsCallFilter, bvltools.TranscriptImporter))
        if options["snvs"]:
            table_specs.append(("SNV", "snvs", SnvsCallFilter, bvltools.SNVImporter))
        if options["gvfs"]:
            table_specs.append(("GVF", "genomic_variome_frequencies", GenomicBvlFrequenciesCallFilter, bvltools.GVFImporter))
        if options["mts"]:
            table_specs.append(("MT", "mts", MtsCallFilter, bvltools.MTImporter))
            table_specs.append(("MT frequency", "mt_variome_frequencies", MtBvlFrequenciesCallFilter, bvltools.MtVariomeFrequencyImporter))
            if options["mt_gnomad_tsv"]:
                table_specs.append(("MT gnomAD frequency", "mt_gnomad_frequencies", MtGnomadFrequenciesCallFilter, bvltools.MtGnomadFrequencyImporter))
        if options["vts"]:
            table_specs.append(("Variant Transcript", "variants_transcripts", VariantsTranscriptsCallFilter, bvltools.VariantTranscriptImporter))
        if options["annotations"]:
            table_specs.append(("Annotation", "variants_annotations", VariantsAnnotationsCallFilter, bvltools.AnnotationImporter))
        if options["consequences"]:
            table_specs.append(("Consequence", "variants_consequences", VariantsConsequencesCallFilter, bvltools.ConsequenceImporter))

        if convert_to_tsv:
            # TSV-only mode: write one TSV file per table, do not touch the database.
            tsv_output_dir = Path(options["tsv_output_dir"])
            tsv_output_dir.mkdir(parents=True, exist_ok=True)

            for _label, table_name, filter_cls, _importer_cls in table_specs:
                table_dir = Path(tsv_output_dir, table_name)
                table_dir.mkdir(parents=True, exist_ok=True)
                _write_to_tsv(make_row_iter(filter_cls), table_name, table_dir)

            # Copy the severities file to the output dir if it exists
            import shutil
            severities_src = Path(options["input_tsv_dir"], "severities.tsv")
            severities_dst = Path(tsv_output_dir, "severities.tsv")
            (shutil.copy(severities_src, severities_dst) and log.info(f"Copied severities file to {severities_dst}")) if severities_src else None
            

            hash_list, hash_map, final_hash = compute_dir_hash(tsv_output_dir)
            log.info("Hash list:\n%s", hash_list)
            log.info("Final hash of output files:\n%s", final_hash)

            compare_dir = options["hash_compare"]
            if compare_dir:
                hash_list2, hash_map2, final_hash2 = compute_dir_hash(compare_dir)
                log.info("Comparison hash list:\n%s", hash_list2)
                log.info("Comparison final hash:\n%s", final_hash2)
                for fname, h in hash_map.items():
                    h2 = hash_map2.get(fname)
                    if h == h2:
                        log.info("File %s hashes match. ✅", fname)
                    else:
                        log.warning("File %s hashes don't match ❌", fname)

            self.stdout.write(f"\nDuration: {bvltools.format_duration(time() - start_time)}")
            return

        # DB import mode
        importer_options = options
        importer_options["path"] = options["input_tsv_dir"]
        importer_options["show_timings"] = self.verbosity >= 3
        importer_options["show_cache_messages"] = self.verbosity >= 3
        if self.verbosity == 1:
            importer_options["progress"] = False

        errors_map = {}
        warnings_map = {}
        counts_map = {}

        last_step_time = time()

        def log_timing(name):
            nonlocal last_step_time
            if self.verbosity >= 3:
                self.stderr.write(f"{name} took {bvltools.format_duration(time() - last_step_time)}")
            last_step_time = time()

        if options["severities"]:
            errors, warnings, counts = bvltools.SeverityImporter(importer_options).import_data()
            log_timing("severities")
            errors_map["Severity"] = errors
            warnings_map["Severity"] = warnings
            counts_map["Severity"] = counts
        for label, _table_name, filter_cls, importer_cls in table_specs:
            try:
                data = make_row_iter(filter_cls)
                importer = importer_cls(importer_options)
                errors_map[label], warnings_map[label], counts_map[label] = importer.import_data(data)
            except Exception as e:
                log.exception("Import failed for %s", label)
                errors_map[label], warnings_map[label], counts_map[label] = (
                    [bvltools.ImportMessage(
                        bvltools.ImportCode.BULK_CREATE_FAILED,
                        f"table import failed and was rolled back: {e}",
                    )],
                    [],
                    None,
                )
            log_timing(label)

        for entity_type, errs in errors_map.items():
            self.log_errors(entity_type, errs)
        for entity_type, warns in warnings_map.items():
            self.log_warnings(entity_type, warns)

        if options["rollback-on-error"] and any(errors_map.values()):
            if self.verbosity >= 2:
                self.stderr.write("\nNot committing transaction (errors)")
            transaction.set_rollback(True)
            status = "ROLLED BACK: operations below were not committed"
        elif options["dry-run"]:
            if self.verbosity >= 2:
                self.stderr.write("\nNot committing transaction (dry-run)")
            transaction.set_rollback(True)
            status = "DRY RUN: operations below were not committed"
        else:
            status = "COMMITTED"

        self.stdout.write(f"\nImport summary ({status})")
        for line in bvltools.format_import_counts(counts_map, errors_map):
            self.stdout.write(line)
        self.stdout.write(f"Duration: {bvltools.format_duration(time() - start_time)}")

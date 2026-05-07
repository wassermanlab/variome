import argparse
import gzip
import hashlib
import io
import json
import logging
import pprint
import sys
from pathlib import Path
from time import time

from django.core.management.base import BaseCommand
from django.db import transaction

import variome_backend.management.tools as bvltools
from variome_backend.management.filters.settings import VcfImportSettings
from variome_backend.management.filters.GenesCallFilter import GenesCallFilter
from variome_backend.management.filters.TranscriptsCallFilter import TranscriptsCallFilter
from variome_backend.management.filters.VariantsCallFilter import VariantsCallFilter
from variome_backend.management.filters.VariantsTranscriptsCallFilter import VariantsTranscriptsCallFilter
from variome_backend.management.filters.VariantsAnnotationsCallFilter import VariantsAnnotationsCallFilter
from variome_backend.management.filters.VariantsConsequencesCallFilter import VariantsConsequencesCallFilter
from variome_backend.management.filters.SnvsCallFilter import SnvsCallFilter
from variome_backend.management.filters.GenomicBvlFrequenciesCallFilter import GenomicBvlFrequenciesCallFilter

log = logging.getLogger("management")


def check_vcf(vcf_path):
    """Check a VCF file (gzipped or plain) for read errors. Logs warnings on failure."""
    import vcfpy
    is_gz = vcf_path.endswith('.gz')
    log.info("Checking VCF file: %s", vcf_path)
    open_func = gzip.open if is_gz else open
    mode = 'rb' if is_gz else 'r'
    n = 0
    last_record = None
    with open_func(vcf_path, mode) as f:
        text_f = io.TextIOWrapper(f, encoding='utf-8') if is_gz else f
        try:
            vcf_reader = vcfpy.Reader(stream=text_f)
            info_fields = " ".join(vcf_reader.header.info_ids())
            log.info("VCF INFO fields:\n%s", info_fields)
            csq = vcf_reader.header.get_info_field_info("CSQ")
            if csq:
                csq_elements = csq.description.split("Format: ")[1]
                csq_fields = " ".join(csq_elements.split("|"))
                log.info("VCF CSQ fields:\n%s", csq_fields)
            else:
                log.info("No CSQ field found in VCF INFO header.")
            for record in vcf_reader:
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
        if errors:
            sys.stderr.write(f"\nERRORS ({len(errors)}) in {entity_type} load:\n")
            for line in bvltools.format_errors(errors, log_all=self.log_all_errors):
                sys.stderr.write(line + "\n")

    def log_warnings(self, entity_type, warnings):
        if warnings:
            sys.stderr.write(f"\nWARNINGS ({len(warnings)}) in {entity_type} load:\n")
            for line in bvltools.format_messages(warnings, log_all=self.log_all_errors):
                sys.stderr.write(line + "\n")

    def add_arguments(self, parser):
        parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

        # --- VCF source ---
        parser.add_argument(
            "--vcf",
            dest="vcf_file",
            required=True,
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
            help="Prefix chromosome names with 'chr'",
        )
        parser.add_argument(
            "--out-hyphens",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Use hyphens in variant IDs (e.g. 1-100-A-G); use underscores when disabled",
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
        transaction.set_autocommit(False)
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

        check_vcf(vcf_file)

        # Helper that returns a row generator for the given filter class
        def make_row_iter(filter_cls, **filter_kwargs):
            return filter_cls(vcf_file, settings, **filter_kwargs).getTableRows()

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

            end_time = time()
            elapsed = end_time - start_time
            sys.stdout.write(
                f"\n\nElapsed time: {elapsed // 3600:.0f} hours "
                f"{(elapsed % 3600) // 60:.0f} minutes "
                f"{elapsed % 60:.1f} seconds\n"
            )
            return

        # DB import mode
        importer_options = {
            "path": options["input_tsv_dir"],
            "progress": options["progress"],
            "failfast": options["failfast"],
            "ignore-existing": options["ignore-existing"],
            "batch": options["batch"],
            "delete": options["delete"],
        }

        errors_map = {}
        warnings_map = {}
        counts_map = {}

        last_step_time = time()

        def log_timing(name):
            nonlocal last_step_time
            duration = time() - last_step_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = duration % 60
            log.info("%s took %dh %dm %.1fs", name, hours, minutes, seconds)
            last_step_time = time()

        if options["severities"]:
            errors, warnings, counts = bvltools.SeverityImporter(importer_options).import_data()
            log_timing("severities")
            errors_map["Severity"] = errors
            warnings_map["Severity"] = warnings
            counts_map["Severity"] = counts
        for label, _table_name, filter_cls, importer_cls in table_specs:
            errors_map[label], warnings_map[label], counts_map[label] = (
                importer_cls(importer_options).import_data(make_row_iter(filter_cls))
            )
            log_timing(label)

        for entity_type, errs in errors_map.items():
            self.log_errors(entity_type, errs)
        for entity_type, warns in warnings_map.items():
            self.log_warnings(entity_type, warns)

        if options["rollback-on-error"]:
            if any(errors_map.values()):
                sys.stderr.write("\nNot committing transaction (errors)\n")
                transaction.rollback()
                return

        if options["dry-run"]:
            sys.stderr.write("\nNot committing transaction (dry-run)\n")
            transaction.rollback()
        else:
            transaction.commit()

        def report_counts(model, counts):
            if counts:
                total, success = counts
                percent = round(100 * success / total, 5) if total else 100
                sys.stdout.write(f"\n{model}: {success} out of {total}: {percent} %")
                
        for entity_type, counts in counts_map.items():
            report_counts(entity_type, counts)

        end_time = time()
        elapsed = end_time - start_time
        sys.stdout.write(
            f"\n\nElapsed time: {elapsed // 3600:.0f} hours "
            f"{(elapsed % 3600) // 60:.0f} minutes "
            f"{elapsed % 60:.1f} seconds\n"
        )

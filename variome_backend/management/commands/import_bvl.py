import logging
import pprint
import argparse
import sys
from time import time

from django.core.management.base import BaseCommand
from django.db import transaction

import variome_backend.management.import_tools as bvltools

log = logging.getLogger("management")


class Command(BaseCommand):
    help = "Import bvl data from tsv files"
    enable_debug = False
    verbose = False

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
        parser.add_argument(
            "--path",
            "-p",
            dest="path",
            required=False,
            default="data/fixtures",
            help="Path of folder containing unpacked bvl data files",
        )
        parser.add_argument(
            "--severities",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import severities from supplied data?",
        )
        parser.add_argument(
            "--genes",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import genes from supplied data?",
        )
        parser.add_argument(
            "--variants",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import variants from supplied data?",
        )
        parser.add_argument(
            "--transcripts",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import transcripts from supplied data?",
        )
        parser.add_argument(
            "--snvs",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import SNVs from supplied data?",
        )
        parser.add_argument(
            "--gvfs",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import GVFs from supplied data?",
        )
        parser.add_argument(
            "--ggfs",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import GGFs from supplied data?",
        )
        parser.add_argument(
            "--annotations",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import variant annotations from supplied data?",
        )
        parser.add_argument(
            "--consequences",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import variant consequences from supplied data?",
        )
        parser.add_argument(
            "--vts",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Import variant transcripts from supplied data?",
        )
        parser.add_argument(
            "--progress",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Show progress indications?",
        )
        parser.add_argument(
            "--failfast",
            "-f",
            default=False,
            action=argparse.BooleanOptionalAction,
            help="Fail on first error?",
        )
        parser.add_argument(
            "--batch",
            default=True,
            action=argparse.BooleanOptionalAction,
            help="Whether to batch database updates in order to improve performance",
        )
        parser.add_argument(
            "--batchsize",
            type=int,
            default=999,
            help= "Batch size for bulk creates - 999 is limit for SQLite, larger numbers may make things faster with PostgreSQL"
        )
        parser.add_argument(
            "--dedupe-cache-window",
            "-c",
            type=int,
            default=10000000,
            help="The size of the window to use when preloading variant position ranges to check existing data when --delete is not used"
        )
        parser.add_argument(
            "--delete",
            default=False,
            action=argparse.BooleanOptionalAction,
            help="Delete the existing data before importing",
        )
        parser.add_argument(
            "--ignore-existing",
            "-i",
            dest="ignore-existing",
            action="store_true",
            default=False,
            help="Ignore (don't update) input rows that already exist in the database",
        )
        parser.add_argument(
            "--rollback-on-error",
            "-r",
            dest="rollback-on-error",
            action="store_true",
            default=False,
            help="Rollback (don't commit) database changes on errors",
        )
        parser.add_argument(
            "--dry-run",
            "-n",
            dest="dry-run",
            action="store_true",
            default=False,
            help="Dry run - make no changes to database",
        )
        parser.add_argument(
            "--log-all-errors",
            dest="log_all_errors",
            action="store_true",
            default=False,
            help="Print every error in full; by default only the first 10 per error group are shown",
        )

    @transaction.atomic
    def handle(self, **options):
        log.debug("import_bvl got options: \n %s", pprint.pformat(options))
        start_time = time()
        self.log_all_errors = options["log_all_errors"]

        last_step_time = time()

        def log_timing(name):
            nonlocal last_step_time
            duration = time() - last_step_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = duration % 60
            log.info("%s took %dh %dm %.1fs", name, hours, minutes, seconds)
            last_step_time = time()

        sev_errors = None
        gen_errors = None
        var_errors = None
        tra_errors = None
        snv_errors = None
        gvf_errors = None
        ggf_errors = None
        vts_errors = None
        ann_errors = None
        con_errors = None
        sev_warnings = None
        gen_warnings = None
        var_warnings = None
        tra_warnings = None
        snv_warnings = None
        gvf_warnings = None
        ggf_warnings = None
        vts_warnings = None
        ann_warnings = None
        con_warnings = None
        sev_counts = None
        gen_counts = None
        var_counts = None
        tra_counts = None
        snv_counts = None
        gvf_counts = None
        ggf_counts = None
        vts_counts = None
        ann_counts = None
        con_counts = None

        options['out_hyphens'] = True
        # too fragile to allow customizing the variant id delimiter right now
        # variant_id is used in joins across TSVs in the output script(s)
        # so it's natural to follow the TSV input instead of using a flag
        # TODO - test with underscore-delimited variant_id TSVs (ibvl's format)

        if options["severities"]:
            sev_errors, sev_warnings, sev_counts = bvltools.SeverityImporter(
                options
            ).import_data()
            log_timing("severities")

        if options["genes"]:
            gen_errors, gen_warnings, gen_counts = bvltools.GeneImporter(
                options
            ).import_data()
            log_timing("genes")

        if options["variants"]:
            var_errors, var_warnings, var_counts = bvltools.VariantImporter(
                options
            ).import_data()
            log_timing("variants")

        if options["transcripts"]:
            tra_errors, tra_warnings, tra_counts = bvltools.TranscriptImporter(
                options
            ).import_data()
            log_timing("transcripts")

        if options["snvs"]:
            snv_errors, snv_warnings, snv_counts = bvltools.SNVImporter(
                options
            ).import_data()
            log_timing("snvs")

        if options["gvfs"]:
            gvf_errors, gvf_warnings, gvf_counts = bvltools.GVFImporter(
                options
            ).import_data()
            log_timing("gvfs")

        if options["ggfs"]:
            ggf_errors, ggf_warnings, ggf_counts = bvltools.GGFImporter(
                options
            ).import_data()
            log_timing("ggfs")

        if options["vts"]:
            vts_errors, vts_warnings, vts_counts = bvltools.VariantTranscriptImporter(
                options
            ).import_data()
            log_timing("variant transcripts")

        if options["annotations"]:
            ann_errors, ann_warnings, ann_counts = bvltools.AnnotationImporter(
                options
            ).import_data()
            log_timing("annotations")

        if options["consequences"]:
            con_errors, con_warnings, con_counts = bvltools.ConsequenceImporter(
                options
            ).import_data()
            log_timing("consequences")

        self.log_errors("Severity", sev_errors)
        self.log_errors("Gene", gen_errors)
        self.log_errors("Variant", var_errors)
        self.log_errors("Transcript", tra_errors)
        self.log_errors("SNV", snv_errors)
        self.log_errors("GVF", gvf_errors)
        self.log_errors("GGF", ggf_errors)
        self.log_errors("Variant Transcript", vts_errors)
        self.log_errors("Annotation", ann_errors)
        self.log_errors("Consequence", con_errors)

        self.log_warnings("Severity", sev_warnings)
        self.log_warnings("Gene", gen_warnings)
        self.log_warnings("Variant", var_warnings)
        self.log_warnings("Transcript", tra_warnings)
        self.log_warnings("SNV", snv_warnings)
        self.log_warnings("GVF", gvf_warnings)
        self.log_warnings("GGF", ggf_warnings)
        self.log_warnings("Variant Transcript", vts_warnings)
        self.log_warnings("Annotation", ann_warnings)
        self.log_warnings("Consequence", con_warnings)

        status = "COMMITTED"
        if options["rollback-on-error"]:
            if (
                sev_errors
                or gen_errors
                or var_errors
                or tra_errors
                or snv_errors
                or gvf_errors
                or ggf_errors
                or ann_errors
                or con_errors
                or vts_errors
            ):
                sys.stderr.write("\nNot committing transaction (errors)\n")
                transaction.set_rollback(True)
                status = "ROLLED BACK: operations below were not committed"

        # if dry run, rollback transaction
        if options["dry-run"] and status == "COMMITTED":
            sys.stderr.write("\nNot committing transaction (dry-run)\n")
            transaction.set_rollback(True)
            status = "DRY RUN: operations below were not committed"

        self.stdout.write(f"\nImport summary ({status})")

        results = [
            ("Severity", sev_counts, sev_errors),
            ("Gene", gen_counts, gen_errors),
            ("Variant", var_counts, var_errors),
            ("Transcript", tra_counts, tra_errors),
            ("SNV", snv_counts, snv_errors),
            ("GVF", gvf_counts, gvf_errors),
            ("GGF", ggf_counts, ggf_errors),
            ("Variant Transcript", vts_counts, vts_errors),
            ("Annotation", ann_counts, ann_errors),
            ("Consequence", con_counts, con_errors),
        ]
        counts_map = {name: counts for name, counts, _ in results if counts is not None}
        errors_map = {name: errors for name, _, errors in results}
        for line in bvltools.format_import_counts(counts_map, errors_map):
            self.stdout.write(line)

        self.stdout.write(f"Duration: {bvltools.format_duration(time() - start_time)}")
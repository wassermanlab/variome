import logging
import pprint
import argparse
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

import variome_backend.management.tools as bvltools

log = logging.getLogger("management")


class Command(BaseCommand):
    help = "Import bvl data from tsv files"
    enable_debug = False
    verbose = False

    def log_errors(self, entity_type, errors):
        if errors:
            sys.stderr.write(f"\nERRORS ({len(errors)}) in {entity_type} load:\n")
            for err in errors:
                sys.stderr.write(f"* {err}\n")

    def log_warnings(self, entity_type, warnings):
        if warnings:
            sys.stderr.write(f"\nWARNINGS ({len(warnings)}) in {entity_type} load:\n")
            for err in warnings:
                sys.stderr.write(f"* {err}\n")

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

    def handle(self, **options):
        transaction.set_autocommit(False)
        log.debug("import_bvl got options: \n %s", pprint.pformat(options))

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
        

        if options["severities"]:
            sev_errors, sev_warnings, sev_counts = bvltools.SeverityImporter(options).import_data()

        if options["genes"]:
            gen_errors, gen_warnings, gen_counts = bvltools.GeneImporter(options).import_data()

        if options["variants"]:
            var_errors, var_warnings, var_counts = bvltools.VariantImporter(options).import_data()

        if options["transcripts"]:
            tra_errors, tra_warnings, tra_counts = bvltools.TranscriptImporter(
                options
            ).import_data()

        if options["snvs"]:
            snv_errors, snv_warnings, snv_counts = bvltools.SNVImporter(options).import_data()

        if options["gvfs"]:
            gvf_errors, gvf_warnings, gvf_counts = bvltools.GVFImporter(options).import_data()

        if options["ggfs"]:
            ggf_errors, ggf_warnings, ggf_counts = bvltools.GGFImporter(options).import_data()

        if options["vts"]:
            vts_errors, vts_warnings, vts_counts = bvltools.VariantTranscriptImporter(
                options
            ).import_data()

        if options["annotations"]:
            ann_errors, ann_warnings, ann_counts = bvltools.AnnotationImporter(
                options
            ).import_data()

        if options["consequences"]:
            con_errors, con_warnings, con_counts = bvltools.ConsequenceImporter(
                options
            ).import_data()

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
                transaction.rollback()
                return

        # if dry run, rollback transaction
        if options["dry-run"]:
            sys.stderr.write("\nNot committing transaction (dry-run)\n")
            transaction.rollback()
        else:
            transaction.commit()
            
        def report_counts(model, counts):
            if counts:
                (total, success) = counts
                if total == 0:
                    percent = 100
                else:
                    percent = round(100 * success / total, 5)
                sys.stdout.write(f"\n{model}: {success} out of {total}: {percent} %")
            
        report_counts("Severity", sev_counts)
        report_counts("Gene", gen_counts)
        report_counts("Variant", var_counts)
        report_counts("Transcript", tra_counts)
        report_counts("SNV", snv_counts)
        report_counts("GVF", gvf_counts)
        report_counts("GGF", ggf_counts)
        report_counts("Variant Transcript", vts_counts)
        report_counts("Annotation", ann_counts)
        report_counts("Consequence", con_counts)

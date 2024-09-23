import logging
import pprint
import argparse
import sys
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

import ibvl.library.models as ibvlmodels
import ibvl.management.tools as ibvltools

log = logging.getLogger("management")


class Command(BaseCommand):
    help = "Import IBVL data from tsv files"
    enable_debug = False
    verbose = False

    def log_errors(self, entity_type, errors):
        if errors:
            sys.stderr.write(f"\nERRORS ({len(errors)}) in {entity_type} load:\n")
            for err in errors:
                sys.stderr.write(f"* {err}\n")

    def add_arguments(self, parser):
        parser.formatter_class=argparse.ArgumentDefaultsHelpFormatter
        parser.add_argument(
            "--path", "-p", dest="path", required=True,
            help="Path of folder containing unpacked IBVL data files",
        )
        parser.add_argument(
            "--severities", default=True, action=argparse.BooleanOptionalAction,
            help="Import severities from supplied data?",
        )
        parser.add_argument(
            "--genes", default=True, action=argparse.BooleanOptionalAction,
            help="Import genes from supplied data?",
        )
        parser.add_argument(
            "--variants", default=True, action=argparse.BooleanOptionalAction,
            help="Import variants from supplied data?",
        )
        parser.add_argument(
            "--transcripts", default=True, action=argparse.BooleanOptionalAction,
            help="Import transcripts from supplied data?",
        )
        parser.add_argument(
            "--snvs", default=True, action=argparse.BooleanOptionalAction,
            help="Import SNVs from supplied data?",
        )
        parser.add_argument(
            "--gvfs", default=True, action=argparse.BooleanOptionalAction,
            help="Import GVFs from supplied data?",
        )
        parser.add_argument(
            "--ggfs", default=True, action=argparse.BooleanOptionalAction,
            help="Import GGFs from supplied data?",
        )
        parser.add_argument(
            "--annotations", default=True, action=argparse.BooleanOptionalAction,
            help="Import variant annotations from supplied data?",
        )
        parser.add_argument(
            "--consequences", default=True, action=argparse.BooleanOptionalAction,
            help="Import variant consequences from supplied data?",
        )
        parser.add_argument(
            "--vts", default=True, action=argparse.BooleanOptionalAction,
            help="Import variant transcripts from supplied data?",
        )
        parser.add_argument(
            "--progress", default=True, action=argparse.BooleanOptionalAction,
            help="Show progress indications?",
        )
        parser.add_argument(
            "--failfast", "-f", default=False, action=argparse.BooleanOptionalAction,
            help="Fail on first error?",
        )
        parser.add_argument(
            "--batch", "-b", dest="batch", action="store_true", default=False,
            help="Batch database updates to attempt to improve performance",
        )
        parser.add_argument(
            "--ignore-existing", "-i", dest="ignore-existing", action="store_true", default=False,
            help="Ignore (don't update) input rows that already exist in the database",
        )
        parser.add_argument(
            "--rollback-on-error", "-r", dest="rollback-on-error", action="store_true", default=False,
            help="Rollback (don't commit) database changes on errors",
        )
        parser.add_argument(
            "--dry-run", "-n", dest="dry-run", action="store_true", default=False,
            help="Dry run - make no changes to database",
        )

    def handle(self, **options):
        transaction.set_autocommit(False)
        log.debug("import_ibvl got options: \n %s", pprint.pformat(options))

        sev_errors = None
        gen_errors = None
        var_errors = None
        tra_errors = None
        snv_errors = None
        gvf_errors = None
        ggf_errors = None
        ann_errors = None
        con_errors = None
        vts_errors = None

        if options['severities']:
            sev_errors = ibvltools.SeverityImporter(options).import_data()

        if options['genes']:
            gen_errors = importer.import_genes()

        if options['variants']:
            var_errors = importer.import_variants()

        if options['transcripts']:
            tra_errors = importer.import_transcripts()

        if options['snvs']:
            snv_errors = ibvltools.SNVImporter(options).import_data()

        if options['gvfs']:
            gvf_errors = importer.import_gvfs()

        if options['ggfs']:
            ggf_errors = importer.import_ggfs()

        if options['annotations']:
            ann_errors = importer.import_annotations()

        if options['consequences']:
            con_errors = importer.import_consequences()

        if options['vts']:
            vts_errors = importer.import_vts()

        self.log_errors("Severity", sev_errors)
        self.log_errors("Gene", gen_errors)
        self.log_errors("Variant", var_errors)
        self.log_errors("Transcript", tra_errors)
        self.log_errors("SNV", snv_errors)
        self.log_errors("GVF", gvf_errors)
        self.log_errors("GGF", ggf_errors)
        self.log_errors("Annotation", ann_errors)
        self.log_errors("Consequence", con_errors)
        self.log_errors("Variant Transcript", vts_errors)

        if options["rollback-on-error"]:
            if (
                sev_errors or gen_errors or var_errors or tra_errors or snv_errors or
                gvf_errors or ggf_errors or ann_errors or con_errors or vts_errors
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
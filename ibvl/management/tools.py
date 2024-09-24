import logging
import csv
import sys
import pprint
from pathlib import Path

from django.db.models import Q

import ibvl.library.models as ibvlmodels

log = logging.getLogger("management")


class IBVLDialect(csv.excel_tab):
    pass


class Importer:
    """ Abstract base class for importers which will import data from .tsv or similar files """
    # Object names for an importer - taken from model._meta if not overridden
    object_name = None
    object_name_plural = None

    # The string to use as a path component in standard input file path
    path_component = None

    # CSV dialect to use (override if a particular importer needs to)
    csv_dialect = IBVLDialect

    # Batch size for bulk creates - 999 is limit for SQLite, larger numbers may make things
    # faster with PostgreSQL
    batch_size = 999

    # Set this when debugging, if you want to stop after a certain number of input rows
    # have been processed
    limit = None

    def __init__(self, options):
        if getattr(self, "model", None) is None:
            raise NotImplementedError("Subclasses of Importer must set 'model' attribute on class")
        if self.object_name is None:
            self.object_name = self.model._meta.verbose_name
        if self.object_name_plural is None:
            self.object_name_plural = self.model._meta.verbose_name_plural

        # Base path to input data
        self.path = Path(options["path"])
        
        # Whether to show progress indication
        self.progress = options["progress"]

        # Whether to bail out after first error
        self.failfast = options["failfast"]

        # Whether to update existing records (else ignore input for rows which exist in DB)
        self.update_existing = not options["ignore-existing"]

        # Whether to use batch mode (it's an order of magnitude or more faster)
        self.batch = options["batch"]

    def get_input_path(self):
        """ Get input path for this data type. May use self.path_component to
        build path """
        if self.path_component is None:
            raise NotImplementedError("Subclass of Importer must set path_component attribute")
        return self.path / self.path_component / f"{self.path_component}.tsv"

    def populate_caches(self):
        """ Populate any caches that will be required during import process """
        pass

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row.
        Default implementation returns input row as-is """
        return True, row

    def import_data(self):
        """ Locate the appropriate data file and load objects from it """
        errors = []
        warnings = []
        input_file = self.get_input_path()
        self.populate_caches()

        with open(input_file, newline="") as f:
            self.reader = csv.DictReader(f, dialect=self.csv_dialect)
            bulk_create = []
            try:
                for row in self.reader:
                    if self.progress and self.reader.line_num % 1000 == 0:
                        sys.stderr.write(f"{self.object_name} {self.reader.line_num}...\n")
                    if self.limit is not None and self.limit < self.reader.line_num:
                        warnings.append(f"stopped processing after limit ({self.limit}) hit")
                        break
                    success, obj = self.clean_data(row)
                    if success:
                        row = obj
                    else:
                        warnings.append(f"ignored row {self.reader.line_num} due to uncleanable data: {obj}")
                        continue
                    if self.batch:
                        if not self.check_existing(row):
                            success, obj = self.created_row_object(row)
                            if success:
                                bulk_create.append(obj)
                            else:
                                errors.append(obj)
                                if self.failfast:
                                    return errors, warnings
                        elif self.update_existing:
                            success, obj = self.update(row)
                            if not success:
                                errors.append(obj)
                                if self.failfast:
                                    return errors, warnings
                    else:
                        success, obj = self.update_or_create(row)
                        if not success:
                            errors.append(obj)
                            if self.failfast:
                                return errors, warnings

                    if len(bulk_create) >= self.batch_size:
                        try:
                            self.model.objects.bulk_create(bulk_create)
                            bulk_create = []
                        except Exception as e:
                            msg = f"error in bulk create of {self.object_name_plural} after input line {self.reader.line_num}: {e}"
                            errors.append(msg)
                            if self.failfast:
                                return errors, warnings
                # Run out of input rows, tidy up outstanding create/updates
                if len(bulk_create):
                    try:
                        self.model.objects.bulk_create(bulk_create)
                        bulk_create = []
                    except Exception as e:
                        msg = f"error in bulk create of {self.object_name_plural} after end of input {self.reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors, warnings
            except csv.Error as e:
                errors.append(f"error reading line {self.reader.line_num}: {e}")
                if self.failfast:
                    return errors, warnings
        return errors, warnings


class SeverityImporter(Importer):
    """ Importer class to locate the severities data file and load severities from it """
    model = ibvlmodels.Severity
    path_component = "severities"

    def get_input_path(self):
        return self.path / f"{self.path_component}.tsv"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        #
        # str() needed as input we're comparing to will be str
        self.existing = {
            str(obj["severity_number"]): obj["pk"]
            for obj in self.model.objects.values("severity_number", "pk")
        }

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["severity_number"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, self.model(
                severity_number=row["severity_number"],
                consequence=row["consequence"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(severity_number=row["severity_number"]).update(
                consequence=row["consequence"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                severity_number=row["severity_number"],
                defaults={
                    "consequence": row["consequence"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} from line {self.reader.line_num}: {e}"
            return False, msg


class GeneImporter(Importer):
    """ Importer class to locate the genes data file and load genes from it """
    model = ibvlmodels.Gene
    path_component = "genes"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["short_name"]: obj["pk"]
            for obj in self.model.objects.values("short_name", "pk")
        }

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["short_name"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, self.model(
                short_name=row["short_name"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # No update possible with single field. No-op.
        return True, 1

    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                short_name=row["short_name"],
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} from line {self.reader.line_num}: {e}"
            return False, msg


class VariantImporter(Importer):
    """ Importer class to locate the variants data file and load variants from it """
    model = ibvlmodels.Variant
    path_component = "variants"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["variant_id"]: obj["pk"]
            for obj in self.model.objects.values("variant_id", "pk")
        }

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["variant_id"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, self.model(
                variant_id=row["variant_id"],
                var_type=row["var_type"],
                filter=row["filter"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(variant_id=row["variant_id"]).update(
                var_type=row["var_type"],
                filter=row["filter"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_id=row["variant_id"],
                defaults={
                    "var_type": row["var_type"],
                    "filter": row["filter"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} from line {self.reader.line_num}: {e}"
            return False, msg


class TranscriptImporter(Importer):
    """ Importer class to locate the transcripts data file and load transcripts from it """
    model = ibvlmodels.Transcript
    path_component = "transcripts"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["transcript_id"]: obj["pk"]
            for obj in self.model.objects.values("transcript_id", "pk")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        self.genes = {
            obj["short_name"]: obj["pk"]
            for obj in ibvlmodels.Gene.objects.values("pk", "short_name")
        }

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["transcript_id"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        gene = self.genes.get(row["gene"], None)
        if gene is None:
            msg = f"error creating {self.object_name} object {row['transcript_id']} for bulk create from line {self.reader.line_num}: gene {row['gene']} not found"
            return False, msg
        try:
            return True, self.model(
                transcript_id=row["transcript_id"],
                gene_id=gene,
                transcript_type=row["transcript_type"],
                tsl=row["tsl"],
                biotype=row["biotype"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object {row['transcript_id']} for bulk create from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(transcript_id=row["transcript_id"]).update(
                gene_id=self.genes[row["gene"]],
                transcript_type=row["transcript_type"],
                tsl=row["tsl"],
                biotype=row["biotype"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for {self.object_name} {row['transcript_id']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object {row['transcript_id']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                transcript_id=row["transcript_id"],
                defaults={
                    "gene_id": self.genes[row["gene"]],
                    "transcript_type": row["transcript_type"],
                    "tsl": row["tsl"],
                    "biotype": row["biotype"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} {row['transcript_id']} from line {self.reader.line_num}: {e}"
            return False, msg


class SNVImporter(Importer):
    """ Importer class to locate the SNV data file and load SNVs from it """
    model = ibvlmodels.SNV
    path_component = "snvs"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["variant__variant_id"]: obj["variant_id"]
            for obj in self.model.objects.values("variant__variant_id", "variant_id")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        self.variants = {
            obj["variant_id"]: obj["pk"]
            for obj in ibvlmodels.Variant.objects.values("pk", "variant_id")
        }

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        for field in (
            "cadd_intr",
            "dbsnp_url",
            "dbsnp_id",
            "ucsc_url",
            "ensembl_url",
            "clinvar_url",
            "gnomad_url",
        ):
            if row[field] == ".":
                row[field] = ""
        for field in (
            "cadd_score",
            "clinvar_vcv",
            "splice_ai"
        ):
            if row[field] == ".":
                row[field] = None
        return True, row

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["variant"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, self.model(
                variant_id=self.variants[row["variant"]],
                type=row["type"],
                length=row["length"],
                chr=row["chr"],
                pos=int(float(row["pos"])),
                ref=row["ref"],
                alt=row["alt"],
                cadd_intr=row["cadd_intr"],
                cadd_score=row["cadd_score"],
                dbsnp_url=row["dbsnp_url"],
                dbsnp_id=row["dbsnp_id"],
                ucsc_url=row["ucsc_url"],
                ensembl_url=row["ensembl_url"],
                clinvar_vcv=row["clinvar_vcv"],
                clinvar_url=row["clinvar_url"],
                gnomad_url=row["gnomad_url"],
                splice_ai=row["splice_ai"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(variant_id=self.variants[row["variant"]]).update(
                type=row["type"],
                length=row["length"],
                chr=row["chr"],
                pos=int(float(row["pos"])),
                ref=row["ref"],
                alt=row["alt"],
                cadd_intr=row["cadd_intr"],
                cadd_score=row["cadd_score"],
                dbsnp_url=row["dbsnp_url"],
                dbsnp_id=row["dbsnp_id"],
                ucsc_url=row["ucsc_url"],
                ensembl_url=row["ensembl_url"],
                clinvar_vcv=row["clinvar_vcv"],
                clinvar_url=row["clinvar_url"],
                gnomad_url=row["gnomad_url"],
                splice_ai=row["splice_ai"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_id=self.variants[row["variant"]],
                defaults={
                    "type": row["type"],
                    "length": row["length"],
                    "chr": row["chr"],
                    "pos": int(float(row["pos"])),
                    "ref": row["ref"],
                    "alt": row["alt"],
                    "cadd_intr": row["cadd_intr"],
                    "cadd_score": row["cadd_score"],
                    "dbsnp_url": row["dbsnp_url"],
                    "dbsnp_id": row["dbsnp_id"],
                    "ucsc_url": row["ucsc_url"],
                    "ensembl_url": row["ensembl_url"],
                    "clinvar_vcv": row["clinvar_vcv"],
                    "clinvar_url": row["clinvar_url"],
                    "gnomad_url": row["gnomad_url"],
                    "splice_ai": row["splice_ai"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg


class GVFImporter(Importer):
    """ Importer class to locate the GVF data file and load GVFs from it """
    model = ibvlmodels.GenomicVariomeFrequency
    path_component = "genomic_variome_frequencies"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["variant__variant_id"]: obj["variant_id"]
            for obj in self.model.objects.values("variant__variant_id", "variant_id")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        self.variants = {
            obj["variant_id"]: obj["pk"]
            for obj in ibvlmodels.Variant.objects.values("pk", "variant_id")
        }

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        for field in (
            "af_tot",
        ):
            if row[field] == ".":
                return False, f"variant {row['variant']}"
        return True, row

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["variant"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            # XXX - the af/ac/an _xx/_xy will appear at some point and need to be added.
            return True, self.model(
                variant_id=self.variants[row["variant"]],
                af_tot=row["af_tot"],
                ac_tot=row["ac_tot"],
                an_tot=row["an_tot"],
                hom_tot=row["hom_tot"],
                hom_xx=row["hom_xx"],
                hom_xy=row["hom_xy"],
                quality=row["quality"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(variant_id=self.variants[row["variant"]]).update(
                af_tot=row["af_tot"],
                ac_tot=row["ac_tot"],
                an_tot=row["an_tot"],
                hom_tot=row["hom_tot"],
                hom_xx=row["hom_xx"],
                hom_xy=row["hom_xy"],
                quality=row["quality"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_id=self.variants[row["variant"]],
                defaults={
                    "af_tot": row["af_tot"],
                    "ac_tot": row["ac_tot"],
                    "an_tot": row["an_tot"],
                    "hom_tot": row["hom_tot"],
                    "hom_xx": row["hom_xx"],
                    "hom_xy": row["hom_xy"],
                    "quality": row["quality"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg


class GGFImporter(Importer):
    """ Importer class to locate the GGF data file and load GGFs from it """
    model = ibvlmodels.GenomicGnomadFrequency
    path_component = "genomic_gnomad_frequencies"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            obj["variant__variant_id"]: obj["variant_id"]
            for obj in self.model.objects.values("variant__variant_id", "variant_id")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        self.variants = {
            obj["variant_id"]: obj["pk"]
            for obj in ibvlmodels.Variant.objects.values("pk", "variant_id")
        }

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        for field in (
            "af_tot",
            "ac_tot",
            "an_tot",
            "hom_tot",
        ):
            if row[field] == ".":
                return False, f"variant {row['variant']}"
        return True, row

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["variant"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, self.model(
                variant_id=self.variants[row["variant"]],
                af_tot=row["af_tot"],
                ac_tot=row["ac_tot"],
                an_tot=row["an_tot"],
                hom_tot=row["hom_tot"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(variant_id=self.variants[row["variant"]]).update(
                af_tot=row["af_tot"],
                ac_tot=row["ac_tot"],
                an_tot=row["an_tot"],
                hom_tot=row["hom_tot"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_id=self.variants[row["variant"]],
                defaults={
                    "af_tot": row["af_tot"],
                    "ac_tot": row["ac_tot"],
                    "an_tot": row["an_tot"],
                    "hom_tot": row["hom_tot"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg


class VariantTranscriptImporter(Importer):
    """ Importer class to locate the GGF data file and load GGFs from it """
    model = ibvlmodels.VariantTranscript
    path_component = "variants_transcripts"

    def populate_caches(self):
        self.noexisting = (self.model.objects.count() == 0)
        if not self.noexisting:
            self.current_chromosome = None
            self.existing = {}

        # Too demanding of RAM
        #
        # self.existing = {
        #     (
        #         obj["variant__variant_id"], obj["transcript__transcript_id"]
        #     ): (
        #         obj["pk"]
        #     )
        #     for obj in self.model.objects.values(
        #         "variant__variant_id",
        #         "transcript__transcript_id",
        #         "pk"
        #     )
        # }

        self.variants = {
            obj["variant_id"]: obj["pk"]
            for obj in ibvlmodels.Variant.objects.values("pk", "variant_id")
        }
        self.transcripts = {
            obj["transcript_id"]: obj["pk"]
            for obj in ibvlmodels.Transcript.objects.values("pk", "transcript_id")
        }

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        novariant = False
        notranscript = False
        if row["variant"] == "":
            novariant = True
        if row["transcript"] == "":
            notranscript = True
        if novariant and notranscript:
            return False, "variant and transcript missing from input"
        if novariant:
            return False, f"transcript {row['transcript']} but variant missing from input"
        if notranscript:
            return False, f"variant {row['variant']} but transcript missing from input"
        return True, row

    def cache_chromosome(self, chromosome):
        q = Q(variant__variant_id__startswith=f"{chromosome}-")
        qs = self.model.objects.filter(q).values(
                "variant__variant_id",
                "transcript__transcript_id",
                "pk"
        )
        self.existing = {
            (
                obj["variant__variant_id"], obj["transcript__transcript_id"]
            ): (
                obj["pk"]
            )
            for obj in qs
        }
        self.current_chromosome = chromosome

    def check_existing(self, row):
        """ Return true if row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        if self.noexisting:
            return False
        chromosome, _ = row["variant"].split("-", 1)
        if self.current_chromosome != chromosome:
            self.cache_chromosome(chromosome)
        return (row["variant"], row["transcript"]) in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        variant = self.variants.get(row["variant"], None)
        if variant is None:
            msg = f"error creating {self.object_name} object {row['variant']} / {row['transcript']} for bulk create from line {self.reader.line_num}: variant {row['variant']} not found"
            return False, msg
        transcript = self.transcripts.get(row["transcript"], None)
        if transcript is None:
            msg = f"error creating {self.object_name} object {row['variant']} / {row['transcript']} for bulk create from line {self.reader.line_num}: transcript {row['transcript']} not found"
            return False, msg
        try:
            return True, self.model(
                variant_id=variant,
                transcript_id=transcript,
                hgvsc=row["hgvsc"],
            )
        except Exception as e:
            msg = f"error creating {self.object_name} object for bulk create for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(
                variant_id=self.variants[row["variant"]],
                transcript_id=self.transcripts[row["transcript"]],
            ).update(
                hgvsc=row["hgvsc"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_id=self.variants[row["variant"]],
                transcript_id=self.transcripts[row["transcript"]],
                defaults={
                    "hgvsc": row["hgvsc"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg


class AnnotationImporter(Importer):
    """ Importer class to locate the Variant Annotation data file and load Annotations from it """
    model = ibvlmodels.VariantAnnotation
    path_component = "variants_annotations"

    def populate_caches(self):
        self.noexisting = (self.model.objects.count() == 0)
        if not self.noexisting:
            self.current_chromosome = None
            self.existing = {}
        self.vts = {}

        # Too demanding of RAM
        #
        # self.existing = {
        #     (
        #         obj["variant_transcript__variant__variant_id"], obj["variant_transcript__transcript__transcript_id"]
        #     ): (
        #         obj["pk"]
        #     )
        #     for obj in self.model.objects.values(
        #         "variant_transcript__variant__variant_id",
        #         "variant_transcript__transcript__transcript_id",
        #         "pk"
        #     )
        # }
        # self.vts = {
        #     (obj["variant_id"], obj["transcript_id"]): obj["pk"]
        #     for obj in ibvlmodels.VariantTranscript.objects.values("pk", "variant_id", "transcript_id")
        # }

    def cache_chromosome(self, chromosome):
        q = Q(variant__variant_id__startswith=f"{chromosome}-")
        qs = self.model.objects.filter(q).values(
                "variant__variant_id",
                "transcript__transcript_id",
                "pk"
        )
        self.existing = {
            (
                obj["variant__variant_id"], obj["transcript__transcript_id"]
            ): (
                obj["pk"]
            )
            for obj in qs
        }

        qs = ibvlmodels.VariantTranscript.objects.filter(q).values(
            "pk", "variant_id", "transcript_id"
        )
        self.vts = {
            (obj["variant_id"], obj["transcript_id"]): obj["pk"]
            for obj in qs
        }
        self.current_chromosome = chromosome

    def check_existing(self, row):
        """ Return true if row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        if self.noexisting:
            return False
        chromosome, _ = row["variant"].split("-", 1)
        if self.current_chromosome != chromosome:
            self.cache_chromosome(chromosome)
        return (row["variant"], row["transcript"]) in self.existing

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        if (row["variant"], row["transcript"]) not in self.vts:
            return False, f"variant transcript object not found to annotate variant {row['variant']} transcript {row['transcript']}"
        return row

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        vt = self.vts.get((row["variant"], row["transcript"]), None)
        if vt is None:
            msg = f"variant transcript object not found to annotate variant {row['variant']} transcript {row['transcript']}"
            return False, msg
        try:
            return True, self.model(
                variant_transcript_id=vt,
                hgvsp=row["hgvsp"],
                polyphen=row["polyphen"],
                sift=row["sift"],
                impact=row["impact"],
            )
        except Exception as e:
            msg = f"error creating object for bulk create of {self.object_name} for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(
                variant_transcript_id=self.vts[(row["variant"], row["transcript"])]
            ).update(
                hgvsp=row["hgvsp"],
                polyphen=row["polyphen"],
                sift=row["sift"],
                impact=row["impact"],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_transcript_id=self.vts[(row["variant"], row["transcript"])],
                defaults={
                    "hgvsp": row["hgvsp"],
                    "polyphen": row["polyphen"],
                    "sift": row["sift"],
                    "impact": row["impact"],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg


class ConsequenceImporter(Importer):
    """ Importer class to locate the Variant Consequence data file and load Consequences from it """
    model = ibvlmodels.VariantConsequence
    path_component = "variants_consequences"

    def populate_caches(self):
        self.noexisting = (self.model.objects.count() == 0)
        if not self.noexisting:
            self.current_chromosome = None
            self.existing = {}
        self.vts = {}
        self.severities = {
            obj["severity_number"]: obj["pk"]
            for obj in ibvlmodels.Severity.objects.values("pk", "severity_number")
        }

    def cache_chromosome(self, chromosome):
        q = Q(variant__variant_id__startswith=f"{chromosome}-")
        qs = self.model.objects.filter(q).values(
                "variant__variant_id",
                "transcript__transcript_id",
                "pk"
        )
        self.existing = {
            (
                obj["variant__variant_id"], obj["transcript__transcript_id"]
            ): (
                obj["pk"]
            )
            for obj in qs
        }

        qs = ibvlmodels.VariantTranscript.objects.filter(q).values(
            "pk", "variant_id", "transcript_id"
        )
        self.vts = {
            (obj["variant_id"], obj["transcript_id"]): obj["pk"]
            for obj in qs
        }
        self.current_chromosome = chromosome

    def check_existing(self, row):
        """ Return true if row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        if self.noexisting:
            return False
        chromosome, _ = row["variant"].split("-", 1)
        if self.current_chromosome != chromosome:
            self.cache_chromosome(chromosome)
        return (row["variant"], row["transcript"]) in self.existing

    def clean_data(self, row):
        """ Clean the input data in row & return cleaned row """
        if (row["variant"], row["transcript"]) not in self.vts:
            return False, f"variant transcript object not found for consequence of variant {row['variant']} transcript {row['transcript']}"
        return row

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        vt = self.vts.get((row["variant"], row["transcript"]), None)
        if vt is None:
            msg = f"variant transcript object not found for consequence of variant {row['variant']} transcript {row['transcript']}"
            return False, msg
        severity = self.severities.get(row["severity"], None)
        if severity is None:
            msg = f"severity object with number {row['severity']} not found for consequence of variant {row['variant']} transcript {row['transcript']}"
            return False, msg
        try:
            return True, self.model(
                variant_transcript_id=vt,
                severity=severity,
            )
        except Exception as e:
            msg = f"error creating object for bulk create of {self.object_name} for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = self.model.objects.filter(
                variant_transcript_id=self.vts[(row["variant"], row["transcript"])]
            ).update(
                severity=self.severities[row["severity"]],
            )
            if updated != 1:
                msg = f"error, updated {updated} DB rows for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}"
                return False, msg
            return True, updated
        except Exception as e:
            msg = f"error updating {self.object_name} object for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = self.model.objects.update_or_create(
                variant_transcript_id=self.vts[(row["variant"], row["transcript"])],
                defaults={
                    "severity": self.severities[row["severity"]],
                },
            )
            return True, obj
        except Exception as e:
            msg = f"error creating/updating {self.object_name} for variant {row['variant']} / transcript {row['transcript']} from line {self.reader.line_num}: {e}"
            return False, msg


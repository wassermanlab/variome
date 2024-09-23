import logging
import csv
import sys
import pprint
from pathlib import Path

import ibvl.library.models as ibvlmodels

log = logging.getLogger("management")


class IBVLDialect(csv.excel_tab):
    pass


class Importer:
    path_component = None
    OBJECT_NAME = None
    OBJECT_NAME_PLURAL = None
    CSV_DIALECT = IBVLDialect

    def __init__(self, options):
        if getattr(self, "model", None) is None:
            raise NotImplementedError("Subclasses of Importer must set 'model' attribute on class")
        if self.OBJECT_NAME is None:
            self.OBJECT_NAME = self.model._meta.verbose_name
        if self.OBJECT_NAME_PLURAL is None:
            self.OBJECT_NAME_PLURAL = self.model._meta.verbose_name_plural

        self.path = Path(options["path"])
        self.progress = options["progress"]
        self.failfast = options["failfast"]
        self.update_existing = not options["ignore-existing"]
        self.batch = options["batch"]
        self.batch_size = 999

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
        return row

    def import_data(self):
        """ Locate the appropriate data file and load objects from it """
        errors = []
        input_file = self.get_input_path()
        self.populate_caches()

        with open(input_file, newline="") as f:
            self.reader = csv.DictReader(f, dialect=self.CSV_DIALECT)
            bulk_create = []
            try:
                for row in self.reader:
                    if self.progress and self.reader.line_num % 1000 == 0:
                        sys.stderr.write(f"{self.OBJECT_NAME} {self.reader.line_num}...\n")
                    row = self.clean_data(row)
                    if self.batch:
                        if not self.check_existing(row):
                            success, obj = bulk_create.append(self.created_row_object())
                            if not success:
                                errors.append(obj)
                                if self.failfast:
                                    return errors
                        elif self.update_existing:
                            success, obj = self.update(row)
                            if not success:
                                errors.append(obj)
                                if self.failfast:
                                    return errors
                    else:
                        success, obj = self.update_or_create(row)
                        if not success:
                            errors.append(obj)
                            if self.failfast:
                                return errors

                    if len(bulk_create) >= self.batch_size:
                        try:
                            self.model.objects.bulk_create(bulk_create)
                            bulk_create = []
                        except Exception as e:
                            msg = f"error in bulk create of {self.OBJECT_NAME_PLURAL} after input line {self.reader.line_num}: {e}"
                            errors.append(msg)
                            if self.failfast:
                                return errors
                # Run out of input rows, tidy up outstanding create/updates
                if len(bulk_create):
                    try:
                        self.model.objects.bulk_create(bulk_create)
                        bulk_create = []
                    except Exception as e:
                        msg = f"error in bulk create of {self.OBJECT_NAME_PLURAL} after end of input {self.reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {self.reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors

    def import_severities(self):
        """ Locate the severities data file and load severities from it """
        errors = []
        input_file = self.path / "severities.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Severity {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.Severity.objects.update_or_create(
                            severity_number=row['severity_number'],
                            defaults={
                                "consequence": row['consequence'],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating severity {row['severity_number']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors

    def import_genes(self):
        """ Locate the genes data file and load genes from it """
        errors = []
        input_file = self.path / "genes" / "genes.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Gene {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.Gene.objects.update_or_create(
                            short_name=row["short_name"],
                        )
                    except Exception as e:
                        msg = f"error creating/updating gene {row['short_name']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors

    def import_variants(self):
        """ Locate the variants data file and load variants from it """
        errors = []
        input_file = self.path / "variants" / "variants.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Variant {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.Variant.objects.update_or_create(
                            variant_id=row["variant_id"],
                            defaults={
                                "var_type": row["var_type"],
                                "filter": row["filter"],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating variant {row['variant_id']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors

            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors

    def import_transcripts(self):
        """ Locate the transcripts data file and load transcripts from it """
        errors = []
        input_file = self.path / "transcripts" / "transcripts.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Transcript {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.Transcript.objects.update_or_create(
                            transcript_id=row["transcript_id"],
                            defaults={
                                "gene": ibvlmodels.Gene.objects.get(short_name=row["gene"]),
                                "transcript_type": row["transcript_type"],
                                "tsl": row["tsl"],
                                "biotype": row["biotype"],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating transcript {row['transcript_id']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors

    def import_snvs(self):
        """ Locate the SNVs data file and load SNVs from it """
        errors = []
        input_file = self.path / "snvs" / "snvs.tsv"

        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        existing = {
            v["variant__variant_id"]: v["variant_id"]
            for v in ibvlmodels.SNV.objects.values("variant__variant_id", "variant_id")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        variants = {
            v["variant_id"]: v["pk"]
            for v in ibvlmodels.Variant.objects.values("pk", "variant_id")
        }

        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            bulk_create = []
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"SNV {reader.line_num}...\n")
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
                    if self.batch:
                        if row["variant"] not in existing:
                            try:
                                bulk_create.append(
                                    ibvlmodels.SNV(
                                        variant_id=variants[row["variant"]],
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
                                )
                            except Exception as e:
                                msg = f"error creating SNV object for bulk create for variant {row['variant']} from line {reader.line_num}: {e}"
                                errors.append(msg)
                                if self.failfast:
                                    return errors
                        elif self.update_existing:
                            try:
                                # This is significantly *faster* than doing bulk updates
                                ibvlmodels.SNV.objects.filter(variant_id=variants[row["variant"]]).update(
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
                                msg = f"error updating SNV object for variant {row['variant']} from line {reader.line_num}: {e}"
                                errors.append(msg)
                                if self.failfast:
                                    return errors
                    else:
                        try:
                            # int(float(foo)) to convert possible scientific notation to int. sucks.
                            obj, created = ibvlmodels.SNV.objects.update_or_create(
                                variant_id=variants[row["variant"]],
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
                        except Exception as e:
                            msg = f"error creating/updating SNV for variant {row['variant']} from line {reader.line_num}: {e}"
                            errors.append(msg)
                            if self.failfast:
                                return errors

                    if len(bulk_create) >= self.batch_size:
                        try:
                            ibvlmodels.SNV.objects.bulk_create(bulk_create)
                            bulk_create = []
                        except Exception as e:
                            msg = f"error in bulk create of SNV after input line {reader.line_num}: {e}"
                            errors.append(msg)
                            if self.failfast:
                                return errors
                # Run out of input rows, tidy up outstanding create/updates
                if len(bulk_create):
                    try:
                        ibvlmodels.SNV.objects.bulk_create(bulk_create)
                        bulk_create = []
                    except Exception as e:
                        msg = f"error in bulk create of SNV after input line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


    def import_gvfs(self):
        """ Locate the GVFs data file and load GVFs from it """
        errors = []
        input_file = self.path / "genomic_variome_frequencies" / "genomic_variome_frequencies.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"GVF {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.GenomicVariomeFrequency.objects.update_or_create(
                            variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
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
                    except Exception as e:
                        msg = f"error creating/updating GVF for variant {row['variant']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


    def import_ggfs(self):
        """ Locate the GGFs data file and load GGFs from it """
        errors = []
        input_file = self.path / "genomic_gnomad_frequencies" / "genomic_gnomad_frequencies.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"GGF {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.GenomicGnomadFrequency.objects.update_or_create(
                            variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
                            defaults={
                                "af_tot": row["af_tot"],
                                "ac_tot": row["ac_tot"],
                                "an_tot": row["an_tot"],
                                "hom_tot": row["hom_tot"],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating GGF for variant {row['variant']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


    def import_annotations(self):
        """ Locate the annotations data file and load annotations from it """
        errors = []
        input_file = self.path / "variants_annotations" / "variants_annotations.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Annotation {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.VariantAnnotation.objects.update_or_create(
                            variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
                            transcript=ibvlmodels.Transcript.objects.get(transcript_id=row["transcript"]),
                            defaults={
                                "hgvsc": row["hgvsc"],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating annotation for variant {row['variant']} transcript {row['transcript']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


    def import_consequences(self):
        """ Locate the consequences data file and load consequences from it """
        errors = []
        input_file = self.path / "variants_consequences" / "variants_consequences.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"Consequence {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.VariantAnnotation.objects.update_or_create(
                            variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
                            transcript=ibvlmodels.Transcript.objects.get(transcript_id=row["transcript"]),
                            defaults={
                                "severity": ibvlmodels.Severity.objects.get(row["severity"]),
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating consequence for variant {row['variant']} transcript {row['transcript']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


    def import_vts(self):
        """ Locate the variant transcripts data file and load VTs from it """
        errors = []
        input_file = self.path / "variants_transcripts" / "variants_transcripts.tsv"
        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            try:
                for row in reader:
                    if self.progress and reader.line_num % 1000 == 0:
                        sys.stderr.write(f"VT {reader.line_num}...\n")
                    try:
                        obj, created = ibvlmodels.VariantTranscript.objects.update_or_create(
                            variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
                            transcript=ibvlmodels.Transcript.objects.get(transcript_id=row["transcript"]),
                            defaults={
                                "hgvsc": row["hgvsc"],
                            },
                        )
                    except Exception as e:
                        msg = f"error creating/updating VT for variant {row['variant']} transcript {row['transcript']} from line {reader.line_num}: {e}"
                        errors.append(msg)
                        if self.failfast:
                            return errors
            except csv.Error as e:
                errors.append(f"error reading line {reader.line_num}: {e}")
                if self.failfast:
                    return errors
        return errors


class SeverityImporter(Importer):
    model = ibvlmodels.Severity
    path_component = "severities"

    def get_input_path(self):
        return self.path / f"{self.path_component}.tsv"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            v["severity_number"]: v["pk"]
            for v in self.model.objects.values("severity_number", "pk")
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
            msg = f"error creating {self.OBJECT_NAME} object for bulk create from line {self.reader.line_num}: {e}"
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
            msg = f"error updating {self.OBJECT_NAME} object from line {self.reader.line_num}: {e}"
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
            msg = f"error creating/updating {self.OBJECT_NAME} from line {self.reader.line_num}: {e}"
            return False, msg


class SNVImporter(Importer):
    model = ibvlmodels.SNV
    path_component = "snvs"

    def populate_caches(self):
        # This costs a bit at startup but is necessary to enable bulk creates, which
        # speed up creation by ~ an order of magnitude
        self.existing = {
            v["variant__variant_id"]: v["variant_id"]
            for v in ibvlmodels.SNV.objects.values("variant__variant_id", "variant_id")
        }
        # This costs around 10s at startup (with 6.5M records) and a bunch of RAM, but
        # approximately doubles the speed of updates
        self.variants = {
            v["variant_id"]: v["pk"]
            for v in ibvlmodels.Variant.objects.values("pk", "variant_id")
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
        return row

    def check_existing(self, row):
        """ Return true is row represents an object that already exists in
        the database (i.e. if update rather than create is needed) """
        return row["variant"] in self.existing

    def created_row_object(self, row):
        """ Create a new object to represent the row supplied.
        Return True, object on success or False, msg on failure """
        try:
            return True, ibvlmodels.SNV(
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
            msg = f"error creating {self.OBJECT_NAME} object for bulk create for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg

    def update(self, row):
        """ Update the existing object in the DB for the supplied row.
        Return True, 1 on success or False, msg on failure """
        # This is significantly *faster* than doing bulk updates
        try:
            updated = ibvlmodels.SNV.objects.filter(variant_id=self.variants[row["variant"]]).update(
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
            msg = f"error updating SNV object for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg
    
    def update_or_create(self, row):
        """ Use foo.objects.update_or_create() to update or create the entry for
        the supplied row in DB.
        Return True, obj on success or False, msg on failure """
        # int(float(foo)) to convert possible scientific notation to int. sucks.
        try:
            obj, created = ibvlmodels.SNV.objects.update_or_create(
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
            msg = f"error creating/updating SNV for variant {row['variant']} from line {self.reader.line_num}: {e}"
            return False, msg

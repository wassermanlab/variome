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
    def __init__(self, options):
        self.path = Path(options["path"])
        self.progress = options["progress"]
        self.failfast = options["failfast"]
        self.update_existing = not options["ignore-existing"]
        self.batch = options["batch"]
        self.batch_size = 999

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

        existing = {
            v["variant__variant_id"]: v["variant_id"]
            for v in ibvlmodels.SNV.objects.values("variant__variant_id", "variant_id")
        }

        with open(input_file, newline="") as f:
            reader = csv.DictReader(f, dialect=IBVLDialect)
            bulk_create = []
            bulk_update = []
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
                                        variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
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
                                snv = ibvlmodels.SNV.objects.get(variant__variant_id=row["variant"])
                                snv.type = row["type"]
                                snv.length = row["length"]
                                snv.chr = row["chr"]
                                snv.pos=int(float(row["pos"]))
                                snv.ref=row["ref"]
                                snv.alt=row["alt"]
                                snv.cadd_intr=row["cadd_intr"]
                                snv.cadd_score=row["cadd_score"]
                                snv.dbsnp_url=row["dbsnp_url"]
                                snv.dbsnp_id=row["dbsnp_id"]
                                snv.ucsc_url=row["ucsc_url"]
                                snv.ensembl_url=row["ensembl_url"]
                                snv.clinvar_vcv=row["clinvar_vcv"]
                                snv.clinvar_url=row["clinvar_url"]
                                snv.gnomad_url=row["gnomad_url"]
                                snv.splice_ai=row["splice_ai"]
                                bulk_update.append(snv)
                                # ibvlmodels.SNV.objects.filter(variant__variant_id=row["variant"]).update(
                                #     type=row["type"],
                                #     length=row["length"],
                                #     chr=row["chr"],
                                #     pos=int(float(row["pos"])),
                                #     ref=row["ref"],
                                #     alt=row["alt"],
                                #     cadd_intr=row["cadd_intr"],
                                #     cadd_score=row["cadd_score"],
                                #     dbsnp_url=row["dbsnp_url"],
                                #     dbsnp_id=row["dbsnp_id"],
                                #     ucsc_url=row["ucsc_url"],
                                #     ensembl_url=row["ensembl_url"],
                                #     clinvar_vcv=row["clinvar_vcv"],
                                #     clinvar_url=row["clinvar_url"],
                                #     gnomad_url=row["gnomad_url"],
                                #     splice_ai=row["splice_ai"],
                                # )
                            except Exception as e:
                                msg = f"error building SNV object for bulk update for variant {row['variant']} from line {reader.line_num}: {e}"
                                errors.append(msg)
                                if self.failfast:
                                    return errors
                    else:
                        try:
                            # int(float(foo)) to convert possible scientific notation to int. sucks.
                            obj, created = ibvlmodels.SNV.objects.update_or_create(
                                variant=ibvlmodels.Variant.objects.get(variant_id=row["variant"]),
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
                    if len(bulk_update) >= self.batch_size:
                        try:
                            ibvlmodels.SNV.objects.bulk_update(
                                bulk_update,
                                [
                                    "type",
                                    "length",
                                    "chr",
                                    "pos",
                                    "ref",
                                    "alt",
                                    "cadd_intr",
                                    "cadd_score",
                                    "dbsnp_url",
                                    "dbsnp_id",
                                    "ucsc_url",
                                    "ensembl_url",
                                    "clinvar_vcv",
                                    "clinvar_url",
                                    "gnomad_url",
                                    "splice_ai"
                                ]
                            )
                            bulk_update = []
                        except Exception as e:
                            msg = f"error in bulk update of SNV after input line {reader.line_num}: {e}"
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
                if len(bulk_update):
                    try:
                        ibvlmodels.SNV.objects.bulk_update(
                            bulk_update,
                            [
                                "type",
                                "length",
                                "chr",
                                "pos",
                                "ref",
                                "alt",
                                "cadd_intr",
                                "cadd_score",
                                "dbsnp_url",
                                "dbsnp_id",
                                "ucsc_url",
                                "ensembl_url",
                                "clinvar_vcv",
                                "clinvar_url",
                                "gnomad_url",
                                "splice_ai"
                            ]
                        )
                    except Exception as e:
                        msg = f"error in bulk update of SNV after input line {reader.line_num}: {e}"
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


from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MT_VCF = ROOT / "data" / "fixtures" / "vcf" / "mt.vcf"
NUCLEAR_VCF = Path(__file__).resolve().parent / "fixtures" / "vcf" / "mock_snv.vcf"
IMPORT_NUCLEAR_VCF = ROOT / "data" / "fixtures" / "vcf" / "variome-tiny.vcf"


def create_authenticated_user(client, username="test-user"):
    from django.contrib.auth.models import User

    user = User.objects.create_user(username=username)
    client.force_login(user)
    return user


def select_nuclear_import_record(destination):
    """Keep real chr22:27000075 annotations, excluding unrelated regulatory sites."""
    lines = IMPORT_NUCLEAR_VCF.read_text().splitlines()
    headers = [line for line in lines if line.startswith("#")]
    record = next(line for line in lines if line.startswith("chr22\t27000075\t"))
    destination.write_text("\n".join(headers + [record]) + "\n", encoding="utf-8")


def combine_vcf_fixtures(destination, nuclear_vcf=NUCLEAR_VCF):
    """Keep both fixtures' records, padding nuclear rows with missing MT samples."""
    nuclear = nuclear_vcf.read_text().splitlines()
    mitochondrial = MT_VCF.read_text().splitlines()
    headers = list(
        dict.fromkeys(line for line in nuclear + mitochondrial if line.startswith("##"))
    )
    columns = next(line for line in mitochondrial if line.startswith("#CHROM"))
    nuclear_records = [
        line + "\t.\t.\t.\t." for line in nuclear if line and not line.startswith("#")
    ]
    mt_records = [line for line in mitochondrial if line and not line.startswith("#")]
    destination.write_text(
        "\n".join(headers + [columns] + nuclear_records + mt_records) + "\n",
        encoding="utf-8",
    )


def annotate_mt_for_header_edge_case(destination, nuclear_vcf=NUCLEAR_VCF):
    """Only for CSQ edge cases: add reversed nuclear CSQ to canonical MT 4440."""
    nuclear = nuclear_vcf.read_text().splitlines()
    csq_header = next(line for line in nuclear if line.startswith("##INFO=<ID=CSQ,"))
    prefix, fields = csq_header.rsplit("Format: ", 1)
    reordered_header = (
        prefix + "Format: " + "|".join(fields[:-2].split("|")[::-1]) + '">'
    )
    annotated_record = next(
        line for line in nuclear if not line.startswith("#") and "|Transcript|" in line
    )
    csq = next(
        field.split("=", 1)[1]
        for field in annotated_record.split("\t")[7].split(";")
        if field.startswith("CSQ=")
    )
    reordered_annotations = []
    for annotation in csq.split(","):
        values = annotation.split("|")
        values[0] = "T"
        reordered_annotations.append("|".join(values[::-1]))
    lines = []
    for line in MT_VCF.read_text().splitlines():
        if line.startswith("#CHROM"):
            lines.append(reordered_header)
        if line.startswith("chrM\t4440\t"):
            columns = line.split("\t")
            columns[7] += ";CSQ=" + ",".join(reordered_annotations)
            line = "\t".join(columns)
        lines.append(line)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")

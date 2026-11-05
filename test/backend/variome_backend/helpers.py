from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MT_VCF = ROOT / "data" / "fixtures" / "vcf" / "mt.vcf"
ANNOTATED_MT_VCF = ROOT / "data" / "fixtures" / "vcf" / "mt-annotated.vcf"
NUCLEAR_VCF = ROOT / "data" / "fixtures" / "vcf" / "mock_snv.vcf"
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

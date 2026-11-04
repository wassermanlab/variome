import re
from pathlib import Path

from django.conf import settings
from pyfaidx import Fasta, FastaIndexingError, FetchError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


MAX_SEQUENCE_LENGTH = 200


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reference_sequence(request, region):
    if request.query_params.get("coord_system_version", "GRCh38") != "GRCh38":
        return Response({"error": "Only GRCh38 is available locally."}, status=400)

    # Match chromosome:start..end[:strand], with inclusive 1-based coordinates
    # and optional strand 1 or -1. Bounded fields limit work on untrusted input.
    match = re.fullmatch(
        r"([A-Za-z0-9_.-]{1,100}):([0-9]{1,12})\.\.([0-9]{1,12})(?::(-?1))?",
        region,
    )
    if not match:
        return Response(
            {"error": "Expected chromosome:start..end[:strand]."}, status=400
        )
    chromosome, start, end, strand = match.groups()
    start, end = int(start), int(end)
    if start < 1 or end < start or end - start + 1 > MAX_SEQUENCE_LENGTH:
        return Response(
            {"error": f"Invalid region or region exceeds {MAX_SEQUENCE_LENGTH} bases."},
            status=400,
        )
    chromosome = chromosome.removeprefix("chr")
    if chromosome in ("M", "MT"):
        chromosome = "MT"

    try:
        with Fasta(
            str(Path(settings.REFERENCE_GENOME_PATH).expanduser()),
            build_index=False,
            rebuild=False,
            strict_bounds=True,
            sequence_always_upper=True,
        ) as genome:
            if chromosome not in genome:
                return Response({"error": "Unknown chromosome."}, status=400)
            if end > len(genome[chromosome]):
                return Response(
                    {"error": "Region exceeds chromosome length."}, status=400
                )
            sequence = genome[chromosome][start - 1 : end]
            if strand == "-1":
                sequence = -sequence
            return Response({"seq": str(sequence)})
    except (OSError, ValueError, FastaIndexingError, FetchError):
        return Response(
            {"error": "Local reference unavailable. Run download_reference_genome."},
            status=503,
        )


"""
VCF Import
This module orchestrates the transformation of VCF files and related data sources
into database tables
"""

from typing import Dict, List, Any, Optional

import logging

import gzip
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
from pathlib import Path
import os
import io
import vcfpy
import hashlib
import json
import dotenv
from datetime import datetime

from vcf_import.constants import VCF_FILE, HASH_COMPARE

if not VCF_FILE:
    raise ValueError("VCF_FILE environment variable is not set. Please set it to the path of the input VCF file.")

logger = logging.getLogger(__name__)

from vcf_import.filters.GenesCallFilter import GenesCallFilter
from vcf_import.filters.TranscriptsCallFilter import TranscriptsCallFilter
from vcf_import.filters.VariantsCallFilter import VariantsCallFilter
from vcf_import.filters.VariantsTranscriptsCallFilter import VariantsTranscriptsCallFilter
from vcf_import.filters.VariantsAnnotationsCallFilter import VariantsAnnotationsCallFilter
from vcf_import.filters.VariantsConsequencesCallFilter import VariantsConsequencesCallFilter
from vcf_import.filters.SnvsCallFilter import SnvsCallFilter
from vcf_import.filters.MtsCallFilter import MtsCallFilter
from vcf_import.filters.GenomicBvlFrequenciesCallFilter import GenomicBvlFrequenciesCallFilter
# from vcf_import.filters.GenomicGnomadFrequenciesCallFilter import GenomicGnomadFrequenciesCallFilter
from vcf_import.filters.MtBvlFrequenciesCallFilter import MtBvlFrequenciesCallFilter
# from vcf_import.filters.MtGnomadFrequenciesCallFilter import MtGnomadFrequenciesCallFilter

snv_vcf = VCF_FILE #os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/vcf/variome.vcf')
#snv_vcf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/vcf/mock_snv.vcf')

#os.path.join(os.path.dirname(os.path.abspath(__file__)), '../test_case/crop3.vcf')

mt_vcf = None


# Add a helper to log warnings
def log_warning(message, *args, **kwargs):
    logger.warning(message, *args, **kwargs)

# Utility function to check VCF file for UTF-8 errors (supports gzipped and plain text)
def check_vcf(vcf_path):
    """
    Checks a VCF file (gzipped or not) for UTF-8 errors by iterating through records.
    Logs warnings if errors are found.
    """
    is_gz = vcf_path.endswith('.gz')
    logger.info(f"Checking VCF file: {vcf_path}")
    open_func = gzip.open if is_gz else open
    mode = 'rb' if is_gz else 'r'
    n = 0
    last_record = None
    with open_func(vcf_path, mode) as f:
        if is_gz:
            text_f = io.TextIOWrapper(f, encoding='utf-8')
        else:
            text_f = f
        try:
            vcf_reader = vcfpy.Reader(stream=text_f)
            # Log available INFO fields and CSQ fields before processing
            info_fields = " ".join(vcf_reader.header.info_ids())
            logger.info(f"VCF INFO fields:\n{info_fields}")
            csq = vcf_reader.header.get_info_field_info("CSQ")
            if csq:
                csq_elements = csq.description.split("Format: ")[1]
                csq_fields = " ".join(csq_elements.split("|"))
                logger.info(f"VCF CSQ fields:\n{csq_fields}")
            else:
                logger.info("No CSQ field found in VCF INFO header.")
            for record in vcf_reader:
                n += 1
                last_record = record
                pass  # just iterate to check for errors
        except Exception as e:
            logger.warning(f"Error reading VCF file {vcf_path}: {e}")
            if last_record is not None:
              logger.warning(f"The last successful record was number {n}:")
              logger.warning(f"{last_record}")
              logger.warning("The VCF file will continue to be processed, but this may indicate a problem with the file that could lead to incomplete or incorrect results.")
            else:
              logger.warning("No records were successfully read from the VCF file.")
              exit(1)

class VariantImporter:
    
    def __init__(self):
        pass
    
    def start(self, config: Dict[str, Any]) -> None:
        
        start_time = datetime.now()
        last_now = datetime.now()
        
        def log_timing(name):
            nonlocal last_now
            duration = datetime.now() - last_now
            logger.info(f"{name} took {str(duration)} h:m:s")
            last_now = datetime.now()
            
        results = {}
        output_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        def export_to_tsv(table_name, row_iter):
            output_path = output_dir / f"{table_name}.tsv"
            batch_size = int(os.getenv("TSV_WRITE_BATCH_SIZE", 1000))
            header = None
            with open(output_path, "w", encoding="utf-8") as f:
                batch = []
                for row in row_iter:
                    if header is None:
                        header = row.keys() if isinstance(row, dict) else []
                        f.write("\t".join(header) + "\n")
                    batch.append("\t".join(str(row.get(col, "")) for col in header) + "\n")
                    if len(batch) >= batch_size:
                        f.writelines(batch)
                        batch = []
                if batch:
                    f.writelines(batch)
            logger.info(f"TSV file written: {output_path}")
            
            
        # examine input VCF file for UTF-8 errors (supports gzipped and non-gzipped)
        check_vcf(snv_vcf)

        # Process and export each table one by one to avoid accumulating all in RAM
        genesCallFilter = GenesCallFilter(snv_vcf)
        log_timing("genes (start)")
        export_to_tsv("genes", genesCallFilter.getTableRows())
        log_timing("genes (end)")
        
        transcripts = TranscriptsCallFilter(snv_vcf).getTableRows()
        log_timing("transcripts")
        export_to_tsv("transcripts", transcripts)
        del transcripts

        variants = VariantsCallFilter(snv_vcf).getTableRows()
        log_timing("variants")
        export_to_tsv("variants", variants)
        del variants

        variants_transcripts = VariantsTranscriptsCallFilter(snv_vcf).getTableRows()
        log_timing("variants_transcripts")
        export_to_tsv("variants_transcripts", variants_transcripts)
        del variants_transcripts

        variants_annotations = VariantsAnnotationsCallFilter(snv_vcf).getTableRows()
        log_timing("variants_annotations")   
        export_to_tsv("variants_annotations", variants_annotations)
        del variants_annotations

        variants_consequences = VariantsConsequencesCallFilter(snv_vcf).getTableRows()
        log_timing("variants_consequences")
        export_to_tsv("variants_consequences", variants_consequences)
        del variants_consequences

        snvs = SnvsCallFilter(snv_vcf).getTableRows()
        log_timing("snvs")
        export_to_tsv("snvs", snvs)
        del snvs

        genomic_bvl_frequencies = GenomicBvlFrequenciesCallFilter(snv_vcf).getTableRows()
        log_timing("genomic_bvl_frequencies")
        export_to_tsv("genomic_variome_frequencies", genomic_bvl_frequencies)
        del genomic_bvl_frequencies
        
#        mts_begin = datetime.now()
#        mts = MtsCallFilter(mt_vcf).getTableRows()
#        log_timing("mts", mts_begin)
#        export_to_tsv("mts", mts)
#        del mts
        
#        mtf_begin = datetime.now()
#        mt_bvl_frequencies = MtBvlFrequenciesCallFilter(mt_vcf).getTableRows()
#        log_timing("mt_bvl_frequencies", mtf_begin)
#        export_to_tsv("mt_bvl_frequencies", mt_bvl_frequencies)
#        del mt_bvl_frequencies
        

        logger.info(f"TSV files written to {output_dir}")
        logger.info(f"Processing completed at {datetime.now()}")
        duration = datetime.now() - start_time
        logger.info(f"Total duration: {duration}")
        duration_seconds = duration.total_seconds()
        logger.info(f"Total duration in seconds: {duration_seconds}")
        logger.info(f"total duration in hours:minutes:seconds: {str(duration)}")
        
        def compute_dir_hash(dir_path: str) -> str:
                
            def file_hash(path):
                hasher = hashlib.sha256()
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        hasher.update(chunk)
                return hasher.hexdigest()

            hash_map = {}
            for file in sorted(Path(dir_path).glob("*.tsv")):
                h = file_hash(file)
                hash_map[file.name] = h
                

            # Hash the list of hashes
            final_hasher = hashlib.sha256()
            hash_list_json = json.dumps(hash_map, indent=2)
            
            
            final_hasher.update(hash_list_json.encode('utf-8'))
            final_hash = final_hasher.hexdigest()
            return hash_list_json, hash_map, final_hash
        
        hash_list, m, final_hash = compute_dir_hash(output_dir)
        logger.info(f"Hash list: \n {hash_list}")
        logger.info(f"Final hash of all output files: \n {final_hash}")
        
        if HASH_COMPARE:
        
          hash_list2, m2, final_hash2 = compute_dir_hash(HASH_COMPARE)
          logger.info(f"Hash list 2: \n {hash_list2}")
          logger.info(f"Final hash 2 of all output files: \n {final_hash2}")
          for k, v in m.items():
            hash_list_2_v = m2.get(k)
            if v == hash_list_2_v:
                logger.info(f"File {k} hashes match. ✅")
            else:
                logger.warning(f"File {k} hashes don't match ❌")
        
        def sort_tsv_file(tsv_path):
            """
            Reads a TSV file, sorts lines by the first field, and writes to <filename>_sorted.
            Returns the output file path.
            """
            with open(tsv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return None
            header = lines[0]
            data_lines = lines[1:]
            data_lines_sorted = sorted(data_lines, key=lambda line: line.split("\t", 1)[0])
            out_path = os.path.splitext(tsv_path)[0] + "_sorted.tsv"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(header)
                f.writelines(data_lines_sorted)
            return out_path
            
        
#        for file in m2.keys():
#            sorted_path = sort_tsv_file(os.path.join(os.path.dirname(__file__), "output/benhash", file))
#            logger.info(f"Sorted file written to: {sorted_path}")
        
        
        

def main():
    """Command-line entry point."""
    import argparse
    import pprint
    
    parser = argparse.ArgumentParser(
        description='filter (extract) BVL data out from VCF files and publish to database'
    )
    parser.add_argument('--assembly', choices=['GRCh37', 'GRCh38'],
                       help='Genome assembly', default='GRCh38')
    parser.add_argument('--severity-table', default='data/fixtures/severities.tsv', 
                       help='Path to severity_table.tsv')
    parser.add_argument('--gnomad-snv-tsv', help='Path to gnomAD SNV TSV')
    parser.add_argument('--gnomad-mt-tsv', help='Path to gnomAD MT TSV')
    
    args = parser.parse_args()
    
    config = {
        'assembly': args.assembly,
        'severity_table_path': args.severity_table,
    }
    
    publish_job = VariantImporter()
    publish_job.start(config)
    logger.info("completed")

if __name__ == '__main__':
    main()
# Wasserman Lab BVL

## Dev Environment Setup (Python / Django module)

```
git clone git@github.com:wassermanlab/variome.git
cd variome
```
### 1. Set up project dependencies using preferred method:

#### Option 1 - Uv (recommended)
- Install uv for dependency management (it will be available anywhere on your system, but won't collide with other projects): [https://rye.astral.sh/guide/installation/](https://docs.astral.sh/uv/getting-started/installation/)
- NOTE: example commands in the rest of the document starting with "python" should start with "uv run" instead
- run:

```
uv sync
```

#### Option 2 - Pip
- Setup pip based on your OS and preferred Python environment solution (eg, venv or similar)
- run:
```
pip install -r requirements.lock
```

#### Option 3 - Conda and Pip
```
conda env create -f environment.yaml 
conda activate variome
pip install -r requirements.lock
```

### 2. Set up the database
Postgres is included as an example, but any [database backend supported by Django](https://docs.djangoproject.com/en/5.2/ref/databases/) will work

```
# mac/linux - with homebrew

brew install postgresql (if necessary)
brew services start postgresql (if necessary)
```
```
# windows - with chocolatey

choco install postgresql
net start postgresql

# If psql is not recognized, add PostgreSQL’s bin directory to your PATH environment variable.
# Example: C:\Program Files\PostgreSQL\15\bin

```

```
# Opening psql command line)

# mac / linux

psql

#windows

psql -U postgres
```

```
# commands to enter into psql command interface

CREATE DATABASE variome;
CREATE USER variome WITH PASSWORD 'variome';
GRANT ALL PRIVILEGES on DATABASE variome to variome;
```

### 3. Set up configuration files (.env)
Edit .env DB to match with your database environment, set timezone, other options

```
cp .env-sample .env
```


### 4. Check your installation:
```
python manage.py check
```

or, the UV equivalent:
```
uv run manage.py check
```

It should show something similar to this if it's working:
```
...connecting to postgresql://variome:variome@localhost:5432/variome...
System check identified no issues (0 silenced).
```

### 5. Load the test fixture data and create a superuser account
```
python manage.py migrate
python manage.py import_bvl
python manage.py createsuperuser
```

## Run the Django app

```
python manage.py runserver
```
(optional) - Run on a specific port. If you do, also specify BACKEND_ROOT=http://localhost:8888 in .env so the frontend can talk to the backend properly
```
python manage.py runserver 8888
```


# Frontend setup 

1. Install NodeJS and install the dependencies

```
cd frontend
npm install
```

2. Set up the frontend content files:

```
cp -r public-example content
```

## Run the Frontend

```
cd frontend
npm install
npm run dev
```

It runs at localhost:3000 by default. You can press "o" and hit the enter key in the terminal window to open in a browser easily. Use "h" for more shortcuts

### how to customize the content

You can edit the `frontend/content` files to customize according to branding, access policy information, and any other content.

Markdown format files in the /content folder are treated as full pages, available in the navigation sidebar. You can add more, rename them. To set the icons and sorting order, add them to the IconMap object in content/ContentConfiguration.js.

Markdown format files in /content/Home are individual, "hard-coded" page elements on the Home page, so you shouldn't add more or rename these.

### config reference
PUBLIC_BVL - opens the database for public access, as a demonstration app. For this to work, a shared user account must also be created ( username: `public_demo_user`, email: `public_demo_user@example.com` )


# Importing from a VCF file

Use the `import_bvl_vcf` management command to import data directly from a VCF file into the database.

Mitochondrial records (`M`, `MT`, `chrM` or `chrMT`) are imported into separate
metadata and frequency tables. Both the IBVL tabular MT export and standard
Variome VCF INFO/FORMAT metrics are supported. IDs use `M` consistently.
The supplied `data/fixtures/vcf/mt.vcf` Mutect2 example is also supported,
including sites with multiple alternate alleles. VEP `CSQ` annotations are
optional; without them, gene/transcript annotations and CSQ-derived identifiers
remain absent. `INFO/AN` is retained as supplied. Missing MT-specific cohort
metrics remain null: sample `FORMAT/AF` values are allele fractions, not cohort
frequencies, and are not converted into homoplasmic/heteroplasmic counts or
frequencies.
An optional preprocessed gnomAD mitochondrial TSV can be supplied with
`--mt-gnomad-tsv /path/to/gnomad_mt.tsv`; only variants present in the VCF are
imported. Its columns are `chromosome`, `position`, `ref`, `alt`, `AN`, `AC_hom`,
`AC_het`, `AF_hom`, `AF_het` and `max_observed_heteroplasmy`.
Select an **Example mt** variant in the admin Settings editor to show its link
on the home page.

## Quickstart

```
python manage.py import_bvl_vcf --vcf /path/to/joint.vcf
python manage.py create_indices
```

Run `python manage.py import_bvl_vcf --help` for a full list of options.

The final summary reports per-table input rows processed, rows created,
existing rows updated, rows skipped (ignored existing rows, rejected data, or
pending inserts abandoned on an early stop),
rows failed, and existing rows deleted by `--delete`. These are counts for this
run, not whole-table database totals. "Updated" includes existing rows whose
values were already identical; it is not a count of changed field values.
Bulk creates count only after the insert succeeds. Dry-run and rollback
summaries explicitly mark operations as not committed. Deleted counts exclude
cascaded deletions of related tables.

## Key options

| Option | Default | Description |
|--------|---------|-------------|
| `--vcf` | *(required)* | Path to the input VCF file (plain text or `.gz`) |
| `--input-tsv-dir` | `data/fixtures` | Path to the dir containing severities.tsv |
| `--mts` / `--no-mts` | enabled | Import mitochondrial metadata and cohort frequencies |
| `--mt-gnomad-tsv` | *(none)* | gnomAD mitochondrial frequency TSV to intersect with imported variants |
| `--na` | `.` | Value used to represent missing/null data |
| `--out-chr` | enabled | Prefix chromosome names with `chr` |
| `--out-hyphens` | enabled | Use hyphens in variant IDs (e.g. `1-100-A-G`) if false, uses underscores instead |
| `--cadd-threshold` | `20` | cadd_intr will be classified as "Damaging" if cadd_score is greater than or equal to this number |
| `--default-transcript-source` | `E` | Fallback transcript source when unknown (`E`=Ensembl, `R`=RefSeq) |
| `--ranges` | *(all)* | Restrict processing to specific regions, e.g. `22:27010000-27020000,X:2702000-2802000` |
| `--convert-to-tsv` | disabled | Write TSV files instead of importing into the database |
| `--tsv-output-dir` | `data/vcf_output` | Directory for TSV output (requires `--convert-to-tsv`) |
| `--hash-compare` | *(none)* | Directory of an existing TSV set to compare output hashes against (requires `--convert-to-tsv`) |
| `--dry-run` / `-n` | disabled | Parse and validate without writing to the database |
| `--delete` | disabled | Delete all existing data before importing |
| `--no-genes`, `--no-variants`, etc. | *(all enabled)* | Skip specific tables |

## Comparing output against a reference TSV set

When `--convert-to-tsv` is active, pass `--hash-compare` to verify that the generated TSV files
match a previously known-good set ( this is useful for development of this project, ensuring consistency with legacy tsv-producting tools):

```
python manage.py import_bvl_vcf \
  --vcf /path/to/joint.vcf \
  --convert-to-tsv \
  --tsv-output-dir data/vcf_output \
  --hash-compare data/reference_tsvs
```

Per-file hash differences are reported in the log output.

## Running backend tests

All backend tests (middleware and VCF import filters) live in `test/backend/variome_backend/`.

First, install dev dependencies:

```
uv sync --dev
```

Run all backend tests once:

```
./test.sh -unit -all -v
```

Backend tests run through `test.sh` use an in-memory SQLite database, including when `DB` is set for local PostgreSQL development.

Install browser-test dependencies and Chromium once:

```
cd test/e2e && npm install && npx playwright install chromium
```

Run backend and browser tests with watching and press Enter to rerun on demand:

```
./test.sh
```

Use `./test.sh -e2e`, `./test.sh -unit`, `./test.sh -f test_search.SnvSearchTests`, or `./test.sh -f home.spec.mjs` to target a suite or test. E2E ports and timeout can be configured with `E2E_BACKEND_PORT`, `E2E_FRONTEND_PORT`, and `-e TIMEOUT_MS`.

### attributions

example DNA image: https://commons.wikimedia.org/wiki/File:202104_Laboratory_instrument_dna.svg

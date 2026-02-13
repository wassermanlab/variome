# Wasserman Lab BVL

## Dev Environment Setup (Python / Django module)

```
git clone git@github.com:wassermanlab/variome.git
cd variome
```

1. Set up dependencies

### Option 1 - Rye (recommended)
install rye for dependency management: https://rye.astral.sh/guide/installation/ then run:

```
rye sync
```

### Option 2 - Pip
```
pip install -R requirements.lock

```

### Option 3 - Conda and Pip
```
conda env create -f environment.yaml 
conda activate variome
pip install -r requirements.lock
```

2. Set up the database
```
brew install postgresql (if necessary)
brew services start postgresql (if necessary) 
psql

CREATE DATABASE variome;
CREATE USER variome WITH PASSWORD 'variome';
GRANT ALL PRIVILEGES on DATABASE variome to variome;
```

3. Set up configuration files (.env)
```
cp .env-sample .env
(edit .env DB to match with your database environment, set timezone, other variables)

```

4. Load the test fixture data and create a superuser account
```
python manage.py migrate
python manage.py import_bvl
python manage.py createsuperuser
```

## Run the Django app

```
python manage.py runserver
```

## Run the Frontend

```
cd frontend
npm install
npm run dev
```


# VCF Publisher (WIP)

Import directly into the database directly from a VCF, no intermediate TSV file step necessary.

Current status: Right now this script writes TSV files as a sanity check to ensure consistency with existing pipeline tsv output

Mitochondrial tables are omitted because these are left out of the currently used vcf reference files

Gnomad information is left out currently because it is easily fetched dynamically from the frontend. However, the value of the bulk gnomad data availability is recognized when it comes to analysis activity, but this is not what the reference library is for as a central feature, so it is not a priority.

## Importing a VCF

```
uv run -m vcf_import.VCF_publish
```
To watch for changes and rerun automatically:

```
uv run watchmedo shell-command --patterns="*.py" --recursive --command='uv run -m vcf_import.VCF_publish'
```


## Testing VCF Importing 


```
uv sync --dev
uv run -m pytest vcf_import/VCF_test.py
```


To watch for changes and rerun tests automatically:

```
uv run watchmedo shell-command --patterns="*.py" --recursive --command='uv run -m pytest vcf_import/VCF_test.py'
```





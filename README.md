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
## Running VCF_test.py (VCF Import Tests)


To run the VCF_import tests using uv and pytest:

```
uv run -m pytest vcf_import/VCF_test.py
```


To watch for changes and rerun tests automatically:

```
uv run watchmedo shell-command --patterns="*.py" --recursive --command='uv run -m pytest vcf_import/VCF_test.py'
```


### Debugging VCF_test.py in VS Code

1. Open the Command Palette (⇧⌘P) and select "Debug: Add Configuration..." if you don't have a launch config.
2. Add the following to your `.vscode/launch.json`:

```
{
	"name": "Debug VCF_test.py",
	"type": "debugpy",
	"request": "launch",
	"program": "${workspaceFolder}/vcf_import/VCF_test.py",
	"console": "integratedTerminal",
	"justMyCode": false
}
```

3. Start debugging by selecting "Debug VCF_test.py" from the Run & Debug panel.

You can use watchmedo for auto-reload, and debug with VS Code using the above configuration.


## Run the Frontend

```
cd frontend
npm install
npm run dev
```


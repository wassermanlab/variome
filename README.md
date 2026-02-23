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
cp -r public-example public
```

## Run the Frontend

```
cd frontend
npm install
npm run dev
```

It runs at localhost:3000 by default. You can press "o" and hit the enter key in the terminal window to open in a browser easily. Use "h" for more shortcuts

### how to customize the content

You can edit the `frontend/public` files to customize according to branding, access policy information, and any other content.

Markdown format files in the /public folder are treated as full pages, available in the navigation sidebar. You can add more, rename them. To set the icons and sorting order, add them to the IconMap object in public/ContentConfiguration.js.

Markdown format files in /public/Home are individual, "hard-coded" page elements on the Home page, so you shouldn't add more or rename these.

### attributions

example DNA image: https://commons.wikimedia.org/wiki/File:202104_Laboratory_instrument_dna.svg

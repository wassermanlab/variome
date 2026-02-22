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
(optional) - Run on a specific port
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
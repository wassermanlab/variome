# He Kākano

The Aotearoa implementation of the Wasserman Lab Background Variant Library web application.

For the general-purpose community version, see the community-version branch: https://github.com/wassermanlab/variome/tree/community-version 

```
git clone -b he-kakano git@github.com:wassermanlab/variome.git
cd variome
```

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
(edit .env DB to match with your database environment, set timezone)

```

4. Load the test fixture data and create a superuser account
```
python manage.py migrate
python manage.py import_bvl
python manage.py createsuperuser
```


5. (for frontend) make config.json file in frontend/src/ that contains the following. Replace 8000 with the port number of the Django app, if necessary
```
{
    "backend_url":"http://localhost:8000/api/",
    "backend_root":"http://localhost:8000/"
}
```

## Run the Django app
```
python manage.py runserver
```
(optional) - Run on a specific port
```
python manage.py runserver 8888
```


## Run the Frontend

```
cd frontend
npm install
npm run dev
```


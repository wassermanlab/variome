An implementation of the Wasserman Lab IBVL portal

## Dev Environment Setup
1. Create an environment for the backend and activate if you did not do it yet
```
install rye for dependency management:
https://rye.astral.sh/guide/installation/

git clone git@github.com:wassermanlab/variome.git
cd variome
rye sync
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

4. Load the data and create a superuser account
```
python manage.py migrate
python manage.py import_ibvl
python manage.py createsuperuser
```


5. (for frontend) make config.json file in frontend/src/ that contains the following. Replace 8000 with the port number of the Django app, if necessary
```
{
    "backend_url":"http://localhost:8000/api/",
    "backend_root":"http://localhost:8000/",
    "frontend_url":"/"
}
```

## Run the Django app
```
rye sync
python manage.py runserver
```

## Run the Frontend

```
cd frontend
npm install
npm run dev
```

Please note the port number that the dev frontend is being run on, you will get CORS errors if the domain is not in the list of CORS_ALLOWED_ORIGINS in ibvl/settings.py L187


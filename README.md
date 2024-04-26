# He Kākano (Variome)
An implementation of the Wasserman Lab IBVL portal

## Dev Environment Setup
1. Create an environment for the backend and activate if you did not do it yet
```
cd path/to/variome-repo
python3 -m venv variome-env
source variome-env/bin/activate
```

2. Install requirements
```
pip install -r requirements.txt

```


3. Set up the database
```
brew install postgresql
brew services start postgresql 
psql

CREATE DATABASE variome;
CREATE USER variome WITH PASSWORD 'variome';
GRANT ALL PRIVILEGES on DATABASE variome to variome;
```

4. Set up configuration files (.env)
```
cp .env-sample .env

```

5. Load the data and create a superuser account
```
python manage.py migrate
python manage.py import_ibvl
python manage.py createsuperuser
```


6. (for frontend) make config.json file in frontend/src/ that contains the following. Replace 8000 with the port number of the Django app, if necessary
```
{
    "backend_url":"http://localhost:8000/api/",
    "backend_root":"http://localhost:8000/",
    "frontend_url":"/"
}
```

## Run the Django app
```
source variome-env/bin/activate
python manage.py runserver
```

## Run the Frontend

```
cd frontend
npm install
npm run dev
```

Please note the port number that the dev frontend is being run on, you will get CORS errors if the domain is not in the list of CORS_ALLOWED_ORIGINS in ibvl/settings.py L187


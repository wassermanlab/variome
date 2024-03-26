# He Kākano (Variome)
An implementation of the Wasserman Lab IBVL portal

## Environment Setup
1. Create an environment for the backend and activate
```
python3 -m venv iembase-env
source iembase-env/bin/activate
```

2. Install requirements
```
pip3 install -r requirements.txt
brew install postgresql

```


3. Set up the database
```
brew services start postgresql
psql

CREATE DATABASE variome;
CREATE USER variome WITH PASSWORD 'variome';
GRANT ALL PRIVILEGES on DATABASE variome to variome;
```

4. Set up configuration file (.env)
```
cp .env-sample .env
```

5. Load the data and create a superuser account
```
python3 manage.py migrate
python3 manage.py import_bvl
python3 manage.py createsuperuser
```


## Run the app
```
source iembase-env/bin/activate
python manage.py runserver
```


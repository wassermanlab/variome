# Variome Project
TODO: Create a description of the project here

## Environment Setup
1. Create an environment for the backend and activate
```
python3 -m venv venv
source venv/bin/activate
```

2. Install requirements
```
pip3 install -r requirements.txt
```

3. Set up the database
```
CREATE DATABASE variome;
CREATE USER variome WITH PASSWORD 'variome';
GRANT ALL PRIVILEGES on DATABASE variome to variome;
```

4. Load the data and create a superuser account
```
python3 manage.py migrate
python3 manage.py loaddata db_dump.json
python3 manage.py createsuperuser
```


## Run the app
```
source venv/bin/activate
python manage.py runserver
```


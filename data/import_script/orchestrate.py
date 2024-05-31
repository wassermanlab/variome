from .do_import import start
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import (
    create_engine,
    event
)

def setup_and_run():
        
    load_dotenv()

    dbConnectionString = os.environ.get("DB")



    print("connecting...")
    engine = create_engine(dbConnectionString, echo=False, pool_pre_ping=True, pool_recycle=3600)

    if database_exists(engine.url):
        #assume already has structure
        pass
    else:
        print("please create your database and run the django migrations before importing the variome library (see readme)")
        engine.dispose()
        quit()

    start(engine)   

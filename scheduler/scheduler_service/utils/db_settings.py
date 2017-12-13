import os
from collections import namedtuple

def create_db_settings():
    db_user = os.getenv('DB_USER') or ''
    db_pass = os.getenv('DB_PASS') or ''
    db_host = os.getenv('DB_HOST') or 'localhost'
    db = os.getenv('DB') or 'test'
    collection = os.getenv('COLLECTION') or 'test'
    if db_user and db_pass:
        db_url = 'mongodb://{}:{}@{}/{}'.format(db_user, db_pass, db_host, db)
    else:
        db_url = 'mongodb://{}/{}'.format(db_host, db)
    settings = namedtuple('settings', 'DB COLLECTION DBURL')
    return settings(DB=db, COLLECTION=collection, DBURL=db_url)
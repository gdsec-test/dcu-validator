import os
from collections import namedtuple


def create_db_settings():
    db_user = os.getenv('DB_USER', '')
    db_pass = os.getenv('DB_PASS', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db = os.getenv('DB', 'devphishstory')
    client_cert = os.getenv("MONGO_CLIENT_CERT", '')
    collection = os.getenv('COLLECTION', 'incidents')
    if db_user and db_pass:
        db_url = f'mongodb://{db_user}:{db_pass}@{db_host}/?authSource={db}&readPreference=primary&directConnection=true&tls=true&tlsCertificateKeyFile={client_cert}'
    else:
        db_url = f'mongodb://{db_host}/{db}'
    settings = namedtuple('settings', 'DB COLLECTION DBURL')
    return settings(DB=db, COLLECTION=collection, DBURL=db_url)

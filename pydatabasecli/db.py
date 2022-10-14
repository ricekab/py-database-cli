from sqlalchemy import create_engine, MetaData

from pydatabasecli.const import PYDBCLI_DATABASE_URL


def get_engine(db_connection_url=PYDBCLI_DATABASE_URL):
    return create_engine(db_connection_url, future=True)


def get_metadata(db_connection_url=PYDBCLI_DATABASE_URL):
    engine = get_engine(db_connection_url=db_connection_url)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    return metadata_obj

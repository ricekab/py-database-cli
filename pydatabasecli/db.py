from sqlalchemy import create_engine, MetaData

from pydatabasecli.const import PYDBCLI_DATABASE_URL
from pydatabasecli.exceptions import PyDBCLIBadConnectionURLError


def get_engine(db_connection_url=PYDBCLI_DATABASE_URL):
    try:
        return create_engine(db_connection_url, future=True)
    except Exception:
        raise PyDBCLIBadConnectionURLError(
            f'Could not connect to database. Is PYDBCLI_DATABASE_URL defined?'
        )


def get_metadata(db_connection_url=PYDBCLI_DATABASE_URL):
    engine = get_engine(db_connection_url=db_connection_url)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)
    return metadata_obj

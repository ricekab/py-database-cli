from sqlalchemy import select, insert

from pydatabasecli.db import get_metadata, get_engine

metadata = get_metadata()
engine = get_engine()

table = metadata.tables['user']
print(type(table))

with engine.connect() as conn:
    stmt = insert(table)
    engine.execute(stmt)

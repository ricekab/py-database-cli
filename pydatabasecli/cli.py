'''
schema
    list-tables  -- show tables
[TABLENAME]
    schema
    insert [...fields...]
    select <id>
    find [...filters...] [--delete]
    delete <pkeys>
'''

import click

from pydatabasecli.db import get_metadata, get_engine

from sqlalchemy import select, insert, delete


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['metadata'] = get_metadata()


def _generate_all_tables_commands(metadata):
    for key, table in metadata.tables.items():
        _generate_table_commands(table)


def _generate_table_commands(table):
    # ---
    # print(table.name)
    # print(type(table))
    # print(dir(table))
    print(table.c)
    print(table.columns)
    print(table.primary_key)
    print(table.primary_key.columns)
    print("---")

    primary_key_names = [c.name for c in table.primary_key.columns]

    # ---
    @click.group(name=table.name,
                 help=f'Perform queries against "{table.name}" table.')
    def _table_cmd_grp():
        pass

    @_table_cmd_grp.command(name='select')
    def _table_select():
        stmt = select(table)
        engine = get_engine()
        with engine.connect() as conn:
            # for row in conn.execute(stmt):
            #     print(row)
            rows = conn.execute(stmt).all()
            print(rows)

    # @click.option('--name')
    def _table_insert(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        stmt = insert(table).values(**kwargs)
        engine = get_engine()
        with engine.connect() as conn:
            res = conn.execute(stmt)
            conn.commit()
            # Mapping returned primary keys.
            # TODO: Unsure if the order is correct! To be tested
            for idx, pkey in enumerate(primary_key_names):
                click.echo(f'{pkey}: {res.inserted_primary_key[idx]}')

    for c in table.columns:
        _table_insert = click.option(
            f'--{c.name}',
            type=c.type.python_type,
        )(_table_insert)
    _table_cmd_grp.command(name='insert')(_table_insert)

    cli.add_command(_table_cmd_grp)


@cli.command(help='List all tables.')
@click.pass_context
def list_tables(ctx):
    metadata_obj = ctx.obj['metadata']
    for t in metadata_obj.tables.keys():
        click.echo(t)


_generate_all_tables_commands(get_metadata())

if __name__ == '__main__':
    cli()

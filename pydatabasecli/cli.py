"""
schema
    list-tables  -- show tables
[TABLENAME]
    schema
    insert [...fields...]
    select <id>
    find [...filters...] [--delete]
    delete <pkeys>

TODO feature list

* Specify custom separator for values via cli option or env var
  (default can remain ','). Useful for insert with long strings that could use
  that symbols.
* Parse option / env var for date, time and, datetime formats. See const.py
"""

import datetime

import click
from sqlalchemy import select, insert, or_, and_

from pydatabasecli import const
from pydatabasecli.db import get_metadata, get_engine


class __NoValue(object):
    """
    Class to differentiate no value given from (the valid) None.
    """
    pass


_no_value = __NoValue()


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
    # ---
    # print(table.c)
    # print(table.columns)
    # print(table.primary_key)
    # print(table.primary_key.columns)
    # print("---")

    primary_key_names = [c.name for c in table.primary_key.columns]

    # TODO: Alias with '_' removed?
    @click.group(name=table.name,
                 help=f'Perform queries against "{table.name}" table.')
    def _table_cmd_grp():
        pass

    # TODO: skip and limit options
    @click.option(
        '--filter-by', '-filter', '-where',
        multiple=True,
        help='''
        Specify fields to filter on in KEY=VALUE,KEY=VALUE,... format .
        
        All key-value pairs specified are combined in an 'AND' clause.
        
        Filter can be specified multiple times, each filter is combined in
        an 'OR' clause.
        
        EXAMPLE
        
        "pydbcli user select -filter name=abc,role=admin -filter id=12"
        
        Generates this statement
        
        SELECT ...
        FROM "user"
        WHERE "user".name = :name_1 AND "user".role = :role_1 OR "user".id = :id_1
        '''.strip())
    def _table_select(filter_by):
        stmt = select(table)
        filter_construct = _parse_filter_option(filter_by)
        stmt = stmt.where(filter_construct)
        engine = get_engine()
        with engine.connect() as conn:
            print(stmt)  # TODO: Debug log statement
            rows = conn.execute(stmt).all()
            # TODO: Display rows with some formatter
            click.echo(rows)

    # TODO: Confirmation & auto-accept prompt
    @click.option(
        '--values', '-values',
        multiple=True,
        help='''
            Specify fields to insert in KEY=VALUE,KEY=VALUE,... format .

            Can be specified multiple times or in one statement. Later
            supplied values override earlier ones.

            EXAMPLE

            "pydbcli user insert -values name=abc,role=admin -values role=user"

            Generates this statement

            INSERT INTO "user" (name, role) VALUES (:name, :role)
            
            With name equal to "abc" and role equal to "user".
            '''.strip())
    def _table_insert(values, **values_dict):
        # Filter out None, explicit None messes with inserted_primary_key
        values_dict = _parse_values_option(values)
        values_dict.update({k: v for k, v in values_dict.items() if v})
        stmt = insert(table).values(**values_dict)
        print(values_dict)  # TODO: Debug log statement
        engine = get_engine()
        with engine.connect() as conn:
            print(stmt)  # TODO: Debug log statement
            res = conn.execute(stmt)
            conn.commit()
            # TODO: Unsure if the order is correct! To be tested
            for idx, pkey in enumerate(primary_key_names):
                click.echo(f'{pkey}: {res.inserted_primary_key[idx]}')

    # TODO: filter + values option
    # TODO: Confirmation & auto-accept prompt
    # TODO: Option to skip 'select' verification
    def _table_update(**kwargs):
        raise NotImplementedError()

    # TODO: filter option
    # TODO: Confirmation & auto-accept prompt
    # TODO: Option to skip 'select' verification
    def _table_delete(**kwargs):
        raise NotImplementedError()

    # CLI decoration
    for c in table.columns:
        # _table_select = click.option(
        #     f'--{c.name}',
        #     type=c.type.python_type,
        #     default=_no_value,
        # )(_table_select)
        _table_insert = click.option(
            f'--{c.name}',
            type=c.type.python_type,
        )(_table_insert)
        # _table_update = click.option(
        #     f'--{c.name}',
        #     type=c.type.python_type,
        #     default=_no_value,
        # )(_table_update)
        # _table_delete = click.option(
        #     f'--{c.name}',
        #     type=c.type.python_type,
        #     default=_no_value,
        # )(_table_delete)
    _table_cmd_grp.command(name='select')(_table_select)
    _table_cmd_grp.command(name='insert')(_table_insert)
    _table_cmd_grp.command(name='update')(_table_update)
    _table_cmd_grp.command(name='delete')(_table_delete)
    cli.add_command(_table_cmd_grp)

    def _parse_filter_option(filter_by_list: list) -> or_:
        """

        :param table: SQLAlchemy table instance for which this filter is parsed.
        :param filter_by_list: List of filter_by clauses. Each entry of the list
            is combined using OR. A single entry may contain multiple keywords,
            separated by ','.

            Example: ['name=myname,role=admin', 'name=other,role=user']
        :return: The sqlalchemy or clause.
        """
        filter_list = list()
        for filter_by_clause in filter_by_list:
            filter_expressions = list()
            for filter_kv_str in filter_by_clause.split(','):
                fragments = filter_kv_str.split('=')
                key = fragments[0]
                value = '='.join(fragments[1:])
                column = getattr(table.c, key)
                filter_expressions.append(column == value)
            filter_list.append(and_(*filter_expressions))
        return or_(*filter_list)

    def _parse_values_option(values: list) -> dict:
        values_dict = dict()
        for values_str in values:
            for kv_str in values_str.split(','):
                fragments = kv_str.split('=')
                key = fragments[0]
                value = '='.join(fragments[1:])
                column = getattr(table.c, key)
                print(f'Data type cast: {column.type.python_type}')
                # TODO: Date // Time // DateTime breaks depending on format
                values_dict[key] = _parse_value_for_type(
                    value, column.type.python_type)
                # values_dict[key] = column.type.python_type(value)
                # values_dict[key] = value
        return values_dict


def _parse_value_for_type(value_str: str, type_):
    """
    Parses a value in string format to an instance of the correct Python type.

    :param value_str:
    :param type_:
    :return:
    """
    if type_ is datetime.datetime:
        return _parse_value_as_datetime(value_str)
    if type_ is datetime.date:
        return _parse_value_as_date(value_str)
    if type_ is datetime.time:
        return _parse_value_as_time(value_str)
    return type_(value_str)


def _parse_value_as_datetime(value_str, format_=const.PYDBCLI_DATETIME_FORMAT):
    """
    Attempt to parse the value as a datetime.

    First we attempt to parse it from ISO format. Failing that, the provided
    format is used to identify it.

    :param value_str:
    :return:
    """
    try:
        return datetime.datetime.fromisoformat(value_str)
    except ValueError:
        pass  # Not isoformat, continue.
    return datetime.datetime.strptime(value_str, format_)


def _parse_value_as_date(value_str):
    raise NotImplementedError()


def _parse_value_as_time(value_str):
    raise NotImplementedError()


@cli.command(help='List all tables.')
@click.pass_context
def list_tables(ctx):
    metadata_obj = ctx.obj['metadata']
    for t in metadata_obj.tables.keys():
        click.echo(t)


_generate_all_tables_commands(get_metadata())

if __name__ == '__main__':
    cli()

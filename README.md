# py-database-cli
A CLI tool to perform basic CRUD operations against a database. 

## Setup

The database connection string can be given as an argument or exposed via
an environment variable (`PYDBCLI_DATABASE_URL`).

## Testing

Declare a local SQLite database:

```
export PYDBCLI_DATABASE_URL=sqlite:///db.sql
```

Use the *createtestmodel.py* script to generate some classes.

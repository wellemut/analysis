import os
from pathlib import Path
from contextlib import contextmanager
import sqlite3
from pypika import Table
from .QueryBuilder import QueryBuilder
import pandas

# Configuration
DATABASES_FOLDER = Path(os.path.join(__file__, "..", "..", "databases")).resolve()


class Database:
    def __init__(self, name, table="default"):
        self.name = name
        self.table = Table(table)

    @property
    def file_path(self):
        return os.path.join(DATABASES_FOLDER, self.name + ".sqlite")

    # def connect(self):
    #     return sqlite3.connect(self.file_path)

    # Start a new insertion query
    def insert(self, **kwargs):
        return (
            QueryBuilder(self)
            .into(self.table)
            .columns(*kwargs.keys())
            .insert(*kwargs.values())
        )

    # Start a new deletion query
    def delete(self, *args, **kwargs):
        return QueryBuilder(self).from_(self.table).delete(*args, **kwargs)

    # Start a new select query
    def select(self, *args, **kwargs):
        return QueryBuilder(self).from_(self.table).select(*args, **kwargs)

    # Create the table in the database with the given columns
    def create(self, *args, **kwargs):
        return QueryBuilder(self).create_table(self.table).columns(*args, **kwargs)

    @contextmanager
    def connect(self):
        try:
            connection = sqlite3.connect(self.file_path)
            yield connection
        finally:
            connection.close()

    # Execute a SQL query. Return true.
    def execute(self, query):
        with self.connect() as connection:
            connection.cursor().execute(query.get_sql())
            connection.commit()
            return True

        # connection = self.connect()
        # connection.cursor.execute(query.get_sql())
        # connection.commit()
        # connection.close()
        # print(query.get_sql())

    # Fetch and return all results for the SQL query.
    def fetch_all(self, query):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            connection.cursor().execute(query.get_sql())
            return connection.cursor().fetchall()

    # Fetch and return a single result for the SQL query.
    def fetch(self, query):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query.get_sql())
            return cursor.fetchone()

    # Fetch and return an array of single values for the SQL query.
    def fetch_values(self, query):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query.get_sql())
            return list(map(lambda x: x[0], cursor.fetchall()))

    # Fetch and return a single value for the SQL query.
    def fetch_value(self, query):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query.get_sql())
            return cursor.fetchone()[0]

    # Load the given columns (array) from the database into a pandas dataframe
    def to_pandas_dataframe(self, *columns):
        connection = sqlite3.connect(
            self.file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES
        )

        dataframe = pandas.read_sql(self.select(*columns).get_sql(), connection)

        connection.close()

        return dataframe

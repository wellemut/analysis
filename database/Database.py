import os
from pathlib import Path
from contextlib import contextmanager
import sqlite3
from .Table import Table
from .QueryBuilder import QueryBuilder
import pandas

# Configuration
DATABASES_FOLDER = Path(os.path.join(__file__, "..", "..", "databases")).resolve()


class Database:
    def __init__(self, name):
        self.name = name

    @property
    def file_path(self):
        return os.path.join(DATABASES_FOLDER, self.name + ".sqlite")

    def table(self, name):
        return Table(database=self, name=name)

    def view(self, *args, **kwargs):
        return self.table(*args, **kwargs)

    @contextmanager
    def connect(self):
        try:
            connection = sqlite3.connect(self.file_path)
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
        finally:
            connection.close()

    @contextmanager
    def start_transaction(self):
        with self.connect() as connection:
            yield connection

    # Execute raw SQL. Return last inserted row ID, if available.
    def execute_sql(self, sql):
        with self.start_transaction() as transaction:
            result = self.execute_sql_in_transaction(transaction=transaction, sql=sql)
            transaction.commit()
            return result

    # Execute a SQL query. Return last inserted row ID, if available.
    def execute(self, query):
        with self.start_transaction() as transaction:
            result = self.execute_in_transaction(transaction=transaction, query=query)
            transaction.commit()
            return result

    # Execute a SQL query within a transaction, without committing.
    # Return last inserted row ID, if available.
    def execute_in_transaction(self, transaction=None, query=None):
        return self.execute_sql_in_transaction(
            transaction=transaction, sql=query.get_sql()
        )

    # Execute raw SQL within a transaction, without committing.
    # Return last inserted row ID, if available.
    def execute_sql_in_transaction(self, transaction=None, sql=None):
        cursor = transaction.cursor()
        cursor.execute(sql)
        return {"lastrowid": cursor.lastrowid}

    # Fetch and return all results for the SQL query.
    def fetch_all(self, query):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(query.get_sql())
            return cursor.fetchall()

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
    def to_dataframe(self, query):
        connection = sqlite3.connect(
            self.file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES
        )

        dataframe = pandas.read_sql(query.get_sql(), connection)

        connection.close()

        return dataframe

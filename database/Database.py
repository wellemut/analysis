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
    def start_transaction(self):
        try:
            connection = sqlite3.connect(self.file_path)
            connection.execute("PRAGMA foreign_keys = ON")
            connection.row_factory = sqlite3.Row
            yield connection
        finally:
            connection.commit()
            connection.close()

    # Continue an existing transaction or a start a new one
    @contextmanager
    def continue_or_start_transaction(self, transaction=None):
        if transaction:
            yield transaction
            return

        with self.start_transaction() as transaction:
            yield transaction

    # Attach another SQLite database instance
    def attach(self, external_db, name, transaction):
        self.execute_sql(
            transaction=transaction,
            sql="""ATTACH DATABASE "%s" AS %s""" % (external_db.file_path, name),
        )

    # Execute raw SQL. Return last inserted row ID and cursor object.
    def execute_sql(self, sql, transaction=None, callback=None):
        with self.continue_or_start_transaction(transaction) as t:
            cursor = t.cursor()
            cursor.execute(sql)

            # Set default callback
            if not callback:
                callback = lambda cursor: {"lastrowid": cursor.lastrowid}

            return callback(cursor)

    # Execute a SQL query.
    def execute(self, query, **kwargs):
        return self.execute_sql(sql=query.get_sql(), **kwargs)

    # Fetch and return all results for the SQL query.
    def all(self, query, **kwargs):
        callback = lambda cursor: cursor.fetchall()
        return self.execute(query=query, callback=callback, **kwargs)

    # Fetch and return a single result for the SQL query.
    def first(self, query, **kwargs):
        callback = lambda cursor: cursor.fetchone()
        return self.execute(query=query, callback=callback, **kwargs)

    # Fetch and return an array of single values for the SQL query.
    def values(self, query, **kwargs):
        callback = lambda cursor: list(map(lambda x: x[0], cursor.fetchall()))
        return self.execute(query=query, callback=callback, **kwargs)

    # Fetch and return a single value for the SQL query.
    def value(self, query, **kwargs):
        callback = lambda cursor: cursor.fetchone()[0]
        return self.execute(query=query, callback=callback, **kwargs)

    # Load the given columns (array) from the database into a pandas dataframe
    def to_dataframe(self, query):
        connection = sqlite3.connect(
            self.file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES
        )

        dataframe = pandas.read_sql(query.get_sql(), connection)

        connection.close()

        return dataframe

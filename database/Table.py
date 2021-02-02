from .QueryBuilder import QueryBuilder
from pypika import Table as PypikaTable


class Table(PypikaTable):
    def __init__(self, name, database=None):
        super().__init__(name)
        self.name = name
        self.database = database

    # Start a new insertion query
    def insert(self, **kwargs):
        # Filter values with None (-> NULL)
        kwargs = dict(filter(lambda x: x[1] is not None, kwargs.items()))

        return (
            QueryBuilder(self.database)
            .into(self.name)
            .columns(*kwargs.keys())
            .insert(*kwargs.values())
        )

    # Start a new deletion query
    def delete(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.name).delete(*args, **kwargs)

    # Start a new select query
    def select(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.name).select(*args, **kwargs)

    # Create the table in the database with the given columns
    def create(self, *args, **kwargs):
        return (
            QueryBuilder(self.database).create_table(self.name).columns(*args, **kwargs)
        )

    # Join the table in the database with another table
    def join(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.name).join(*args, **kwargs)

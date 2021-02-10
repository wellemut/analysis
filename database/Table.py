from .QueryBuilder import QueryBuilder
from pypika import Table as PypikaTable, Schema, functions as fn


class Table(PypikaTable):
    def __init__(self, name, database=None):
        super().__init__(name)
        self.name = name
        self.database = database
        self.table_alias = None
        self.schema_name = None

    # Start a new insertion query
    def insert(self, **kwargs):
        # Filter values with None (-> NULL)
        kwargs = dict(filter(lambda x: x[1] is not None, kwargs.items()))

        return self.insert_in_columns(*kwargs.keys()).insert(*kwargs.values())

    # Start a new insertion query
    def insert_in_columns(self, *columns):
        return QueryBuilder(self.database).into(self.name).columns(*columns)

    # Start a new update query
    def set(self, **kwargs):
        # Filter values with None (-> NULL)
        kwargs = dict(filter(lambda x: x[1] is not None, kwargs.items()))

        query = QueryBuilder(self.database).update(self.name)

        # Run set for each key-value pair
        for key, value in kwargs.items():
            query.set(key, value)

        return query

    def as_(self, table_alias):
        self.table_alias = table_alias
        return self

    def schema(self, schema_name):
        self.schema_name = schema_name
        return self

    @property
    def table(self):
        if self.schema_name:
            return getattr(Schema(self.schema_name), self.name)
        elif self.table_alias:
            return PypikaTable(self.name).as_(self.table_alias)
        else:
            return PypikaTable(self.name)

    # Start a new deletion query
    def delete(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.table).delete(*args, **kwargs)

    # Start a new select query
    def select(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.table).select(*args, **kwargs)

    # Start a new count query
    def count(self, *args, **kwargs):
        return (
            QueryBuilder(self.database)
            .from_(self.table)
            .select(fn.Count(*args, **kwargs))
        )

    # Create the table in the database with the given columns
    def create(self, *args, **kwargs):
        return (
            QueryBuilder(self.database)
            .create_table(self.table)
            .columns(*args, **kwargs)
        )

    # Join the table in the database with another table
    def join(self, *args, **kwargs):
        return QueryBuilder(self.database).from_(self.table).join(*args, **kwargs)

from pypika import Query

# A wrapper around pypika Query, that allows executing the generated SQL on the
# database by calling .execute() or .fetch() or .fetch_all()
class QueryBuilder:
    def __init__(self, database):
        self.database = database
        self.query = Query

    # Delegate all method calls to the pypika Query
    def __getattr__(self, name, *args, **kw):
        def delegator(*args, **kw):
            self.query = getattr(self.query, name)(*args, **kw)
            return self

        return delegator

    def get_sql(self, *args, **kwargs):
        return self.query.get_sql(*args, **kwargs)

    # Needed to support subqueries
    def nodes_(self, *args, **kwargs):
        return self.query.nodes_(*args, **kwargs)

    def execute(self, **kwargs):
        return self.database.execute(query=self, **kwargs)

    def fetch_all(self, **kwargs):
        return self.database.fetch_all(query=self, **kwargs)

    def fetch(self, **kwargs):
        return self.database.fetch(query=self, **kwargs)

    def fetch_values(self, **kwargs):
        return self.database.fetch_values(query=self, **kwargs)

    def fetch_value(self, **kwargs):
        return self.database.fetch_value(query=self, **kwargs)

    def to_dataframe(self):
        return self.database.to_dataframe(self)

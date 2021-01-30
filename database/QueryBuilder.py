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

    def execute(self):
        return self.database.execute(self)

    def execute_in_transaction(self, transaction):
        return self.database.execute_in_transaction(transaction=transaction, query=self)

    def fetch_all(self):
        return self.database.fetch_all(self)

    def fetch(self):
        return self.database.fetch(self)

    def fetch_values(self):
        return self.database.fetch_values(self)

    def fetch_value(self):
        return self.database.fetch_value(self)

    def to_dataframe(self):
        return self.database.to_dataframe(self)

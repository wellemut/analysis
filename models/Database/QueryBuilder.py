from pypika import PostgreSQLQuery as Query

# A wrapper around pypika Query, that allows executing the generated SQL on the
# database by calling .execute() or .first() or .all()
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

    def to_dataframe(self):
        return self.database.to_dataframe(self)


# Delegate several methods to the database
def generate_delegator(func):
    def delegator(self, **kwargs):
        return getattr(self.database, func)(query=self, **kwargs)

    return delegator


for func in ["execute", "all", "first", "values", "value"]:
    setattr(QueryBuilder, func, generate_delegator(func))

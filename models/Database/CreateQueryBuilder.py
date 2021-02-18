import pypika
from pypika import Column
from pypika.queries import CreateQueryBuilder as PypikaCreateQueryBuilder

# Add support for foreign keys to Pypika
class CreateQueryBuilder(PypikaCreateQueryBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._foreign_keys = []

    def foreign_key(self, column, references, on_update=None, on_delete=None):
        self._foreign_keys.append(
            {
                "column": (column if isinstance(column, Column) else Column(column)),
                "references": references,
                "on_update": on_update,
                "on_delete": on_delete,
            }
        )

        return self

    def _foreign_key_clauses(self, **kwargs):
        foreign_key_clauses = []

        for foreign_key in self._foreign_keys:
            foreign_key_clause = (
                "FOREIGN KEY ({column}) REFERENCES {references}".format(
                    column=foreign_key["column"].get_name_sql(**kwargs),
                    references=foreign_key["references"],
                )
            )

            if foreign_key["on_update"] is not None:
                foreign_key_clause += " ON UPDATE {action}".format(
                    action=foreign_key["on_update"]
                )

            if foreign_key["on_delete"] is not None:
                foreign_key_clause += " ON DELETE {action}".format(
                    action=foreign_key["on_delete"]
                )

            foreign_key_clauses.append(foreign_key_clause)

        return foreign_key_clauses

    def _body_sql(self, **kwargs):
        initial_sql = super(CreateQueryBuilder, self)._body_sql(**kwargs)

        clauses = self._foreign_key_clauses(**kwargs)

        return ",".join([initial_sql, *clauses])


pypika.queries.CreateQueryBuilder = CreateQueryBuilder

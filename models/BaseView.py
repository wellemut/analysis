from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.view import create_table_from_selectable
from alembic_utils.pg_view import PGView
import models

# Base class for defining view-only models
# See: https://github.com/olirice/alembic_utils/issues/14#issuecomment-724681447
class BaseView(models.BaseModel):
    __abstract__ = True

    # Keep track of registered views for Alembic
    views = []

    # Disable timestamps mixin
    created_at = None
    updated_at = None

    # Generate __table__ from view query
    @declared_attr
    def __table__(cls):
        view_name = cls.__name__.lower()
        BaseView.register_view(name=view_name, query=cls.__view_query__)
        return create_table_from_selectable(
            name=view_name, selectable=cls.__view_query__.statement
        )

    # Register a PGView with alembic_utils, so that alembic will automatically
    # generate the necessary migrations for our view
    @classmethod
    def register_view(cls, name, query):
        cls.views.append(
            PGView(
                schema="public",
                signature=name,
                definition=str(query.statement.compile(dialect=postgresql.dialect())),
            )
        )
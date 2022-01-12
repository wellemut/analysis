from sqlalchemy import Column

# Monkeypatch SQLAlchemy column to have a #query convenience property that
# equals BaseModel.session.query(Model.column)
# Instead of Model.session.query(Model.id), we can now use Model.id.query
Column.query = property(
    lambda self: get_model_class_from_column(self).session.query(self)
)

# Return the model class associated with an sqlalchemy column
# Based on Query#_only_full_mapper_zero
# See: https://github.com/sqlalchemy/sqlalchemy/blob/a869dc8fe3cd579ed9bab665d215a6c3e3d8a4ca/lib/sqlalchemy/orm/query.py#L211
def get_model_class_from_column(column):
    if "parententity" not in column._annotations:
        raise Exception(f"Could not determine model class from column ${column}")

    return column._annotations["parententity"].class_
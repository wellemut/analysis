from sqlalchemy.orm import Query as BaseQuery


class Query(BaseQuery):
    # Add a convenience method #ids() that returns a list of all IDs
    # Currently, the built-in Query class does not have an option for getting
    # a single column as a flat list. It always returns row objects or tuples.
    def ids(self):
        model = self._only_full_mapper_zero("ids").class_
        return [row.id for row in self.with_entities(model.id).all()]

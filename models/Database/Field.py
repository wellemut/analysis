from pypika import Field
from pypika.terms import BasicCriterion, EmptyCriterion
from pypika.enums import Comparator


class GlobMatching(Comparator):
    glob = " GLOB "


def glob(self, expr):
    return BasicCriterion(GlobMatching.glob, self, self.wrap_constant(expr))


def glob_unless_none(self, expr):
    if expr is None:
        return EmptyCriterion()

    return self.glob(expr)


# Patch the pypika library to support GLOB queries
Field.glob = glob
Field.glob_unless_none = glob_unless_none

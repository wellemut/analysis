from pypika.terms import Criterion, EmptyCriterion, ComplexCriterion
from pypika.enums import Boolean


def __and__(self, other):
    if isinstance(other, EmptyCriterion):
        return self

    return ComplexCriterion(Boolean.and_, self, other)


def __or__(self, other):
    if isinstance(other, EmptyCriterion):
        return self

    return ComplexCriterion(Boolean.or_, self, other)


def __xor__(self, other):
    if isinstance(other, EmptyCriterion):
        return self

    return ComplexCriterion(Boolean.xor_, self, other)


# Patch the pypika library to be able to and/or/xor on an EmptyCriterion
Criterion.__and__ = __and__
Criterion.__or__ = __or__
Criterion.__xor__ = __xor__

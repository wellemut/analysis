from operator import itemgetter
from datetime import datetime
import json
from models.Database import Database, Column, Field
import hashlib

# Simple library for caching function calls/API requests
# The name, method, and args are hashed into a signature. If the signature
# exists in the caching DB, the cached result is returned.
class Cache:
    def __init__(self, name, method, *args, **kwargs):
        self.name = name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.__result = None
        self.__cached_at = None
        self.__loaded = False
        self.__db = Database("cache")
        self.__db_table = self.__db.table("functions")
        self.__db_table.create(
            Column("id", "integer", nullable=False),
            Column("name", "text", nullable=False),
            Column("method", "text", nullable=False),
            Column("args", "text", nullable=False),
            Column("kwargs", "text", nullable=False),
            Column("signature", "text", nullable=False),
            Column("result", "text", nullable=False),
            Column("cached_at", "timestamp", nullable=False),
        ).primary_key("id").unique("signature").if_not_exists().execute()

    @property
    def result(self):
        self.load()
        return json.loads(self.__result or "null")

    @property
    def cached_at(self):
        self.load()
        if self.__cached_at:
            return datetime.fromisoformat(self.__cached_at)
        else:
            return None

    @property
    def is_empty(self):
        self.load()
        return self.__result is None

    @property
    def params(self):
        return {
            "name": self.name,
            "method": self.method,
            "args": json.dumps(self.args),
            "kwargs": json.dumps(self.kwargs),
        }

    @property
    def signature(self):
        return hashlib.sha256(
            bytes(
                json.dumps(self.params),
                encoding="utf-8",
            )
        ).hexdigest()

    def load(self):
        if self.__loaded:
            return

        result, cached_at = itemgetter("result", "cached_at")(
            self.__db_table.select("result", "cached_at")
            .where(Field("signature") == self.signature)
            .limit(1)
            .first()
            or {"result": None, "cached_at": None}
        )

        self.__result = result
        self.__cached_at = cached_at
        self.__loaded = True

    # Update the result in the cache
    def update(self, result):
        result = json.dumps(result)
        cached_at = datetime.isoformat(datetime.utcnow())
        self.__db_table.insert(
            **self.params, signature=self.signature, result=result, cached_at=cached_at
        ).on_conflict(self.__db_table.signature).do_update(
            self.__db_table.result, result
        ).do_update(
            self.__db_table.cached_at, cached_at
        ).execute()

        self.__result = result
        self.__cached_at = cached_at
        self.__loaded = True

import os
import contextvars
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker, Session
from helpers.orm import Query

# Using context var, we get a database session that is unique to the current
# thread
database_session = contextvars.ContextVar("database_session", default=None)
# pool_pre_ping=True is needed for DigitalOcean's $5 droplet to prevent errors
# from the DB connection timing out.
# See: https://stackoverflow.com/a/66515677/6451879
engine = create_engine(os.environ.get("DATABASE_URL"), pool_pre_ping=True)
establish_session = sessionmaker(bind=engine, autocommit=True, query_cls=Query)


# Get the current database session or start a new one
def get_database_session():
    if database_session.get() == None:
        database_session.set(establish_session())

    return database_session.get()


def run_lifecycle_hooks(session, done):
    # If we run any lifecycle hooks, we need to rerun this method, because
    # lifecycle hooks could have added new instances to the session.
    # This flag is used to keep track if any hooks were run.
    rerun = False

    for instance in filter(lambda x: x not in done["new"], session.new):
        instance.on_create()
        done["new"].append(instance)
        rerun = True

    for instance in filter(lambda x: x not in done["dirty"], session.dirty):
        instance.on_update()
        done["dirty"].append(instance)
        rerun = True

    for instance in filter(lambda x: x not in done["deleted"], session.deleted):
        instance.on_delete()
        done["deleted"].append(instance)
        rerun = True

    if rerun:
        run_lifecycle_hooks(session, done)


# Listen for lifecycle events
def orm_lifecycle_events(session, _abc, _def):
    run_lifecycle_hooks(session, {"new": [], "dirty": [], "deleted": []})


listen(Session, "before_flush", orm_lifecycle_events)
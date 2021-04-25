import os
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import hashlib
import json
from config import MAIN_DATABASE
from models.Database import Database, Field, Order
from models import PipelineProgressBar

# Upload analysis database to Fauna
print("Uploading organizations to FaunaDB...")

fauna = FaunaClient(secret=os.environ["FAUNADB_SERVER_KEY"])
db = Database(MAIN_DATABASE)

SCORES = ["total_score", "sdgs_score", *[f"sdg{i}_score" for i in range(1, 18)]]
HANDLES = [f"{social}_handle" for social in ["twitter", "facebook", "linkedin"]]

organization_ids = db.table("organization").select("id").values()

progress = PipelineProgressBar("Upload")

for organization_id in progress.iterate(organization_ids):
    organization = (
        db.view("organization_with_domain")
        .select(
            "domain",
            "homepage",
            "name",
            *SCORES,
            "logo",
            *HANDLES,
            "summary",
            "address",
            "latitude",
            "longitude",
        )
        .where(Field("id") == organization_id)
        .first()
    )

    domain = organization["domain"]

    progress.set_status(f"Uploading {domain}")

    # Prepare data
    data = dict(organization)
    del data["domain"]

    # Create deterministic data hash
    data_hash = hashlib.sha256(
        bytes(
            json.dumps(data),
            encoding="utf-8",
        )
    ).hexdigest()

    # Create or update organization
    exists = fauna.query(q.exists(q.match(q.index("organization_by_domain"), domain)))
    if exists:
        fauna.query(
            q.update(
                q.select(
                    "ref", q.get(q.match(q.index("organization_by_domain"), domain))
                ),
                {
                    "data": {
                        "last_extraction_data": data,
                        "last_extraction_data_hash": data_hash,
                    }
                },
            )
        )

    else:
        fauna.query(
            q.create(
                q.collection("organizations"),
                {
                    "data": {
                        "domain": domain,
                        "last_extraction_data": data,
                        "last_extraction_data_hash": data_hash,
                    }
                },
            )
        )

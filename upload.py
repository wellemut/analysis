import os
from datetime import datetime
import json
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import hashlib
import json
import copy
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
            "commitment_url",
            "alt_commitment_urls",
            *SCORES,
            "logo",
            *HANDLES,
            "about",
            "address",
            "latitude",
            "longitude",
            "state",
            "country",
        )
        .where(Field("id") == organization_id)
        .first()
    )

    domain = organization["domain"]

    progress.set_status(f"Uploading {domain}")

    # Prepare data
    data = dict(organization)
    del data["domain"]
    data["alt_commitment_urls"] = json.loads(data["alt_commitment_urls"])

    # Create deterministic data hash: This hash can be used to determine whether
    # the extracted data for an organization has changed.
    KEYS_TO_SKIP = ["alt_commitment_urls"]
    data_to_hash = copy.deepcopy(data)
    for key in KEYS_TO_SKIP:
        del data_to_hash[key]

    data_hash = hashlib.sha256(
        bytes(
            json.dumps(data_to_hash),
            encoding="utf-8",
        )
    ).hexdigest()

    # Create or update organization
    exists = fauna.query(q.exists(q.match(q.index("organization_by_domain"), domain)))
    if exists:
        fauna.query(
            q.let(
                {
                    "ref": q.select(
                        "ref",
                        q.get(q.match(q.index("organization_by_domain"), domain)),
                    )
                },
                q.do(
                    # Clear last extraction data object, then set new extraction
                    # data. Essentially, this serves as a replace operation.
                    # By default, q.update will merge the properties of two objects,
                    # so if we did not clear it first, we'd end up with old/stale
                    # data in the object.
                    # See https://forums.fauna.com/t/replace-by-path/169/2 for
                    # context.
                    q.update(
                        q.var("ref"),
                        {
                            "data": {
                                "last_extraction_data": None,
                            }
                        },
                    ),
                    q.update(
                        q.var("ref"),
                        {
                            "data": {
                                "last_extraction_data": data,
                                "last_extraction_data_hash": data_hash,
                            }
                        },
                    ),
                ),
            ),
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
                        "created_at": datetime.utcnow()
                        .replace(microsecond=0)
                        .isoformat(),
                    }
                },
            )
        )

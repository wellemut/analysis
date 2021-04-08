# Export analysis database to CSV file
import os
from pathlib import Path
from config import MAIN_DATABASE, EXPORT_DIR
from models.Database import Database, Field, Order

db = Database(MAIN_DATABASE)

print("Exporting organizations to CSV", end="... ", flush=True)

# Load from SQLite
SCORES = ["total_score", "sdgs_score", *[f"sdg{i}_score" for i in range(1, 18)]]
HANDLES = [f"{social}_handle" for social in ["twitter", "facebook", "linkedin"]]

df = (
    db.view("organization_with_domain")
    .select(
        "domain",
        Field("homepage").as_("url"),
        "name",
        *SCORES,
        "logo",
        *HANDLES,
        "summary",
        "address",
        "latitude",
        "longitude",
    )
    .orderby("total_score", order=Order.desc)
    .to_dataframe()
)

# Save
df.to_csv(EXPORT_PATH, index=False)

print("✅")

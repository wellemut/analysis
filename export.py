# Export analysis database to CSV file
import os
from pathlib import Path
from database import Database, Order

EXPORT_PATH = Path(os.path.join(__file__, "..", "export", "database.csv")).resolve()

db = Database("analysis")

print("Exporting", f"{db.name}.sqlite", "to CSV", end="... ", flush=True)

# Load from SQLite
df = (
    db.table("domains")
    .select("*")
    .orderby("total_score", order=Order.desc)
    .to_dataframe()
)

# Drop index
df = df.drop(columns=["id"])

# Save
df.to_csv(EXPORT_PATH, index=False)

print("✅")

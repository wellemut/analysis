import os
from pathlib import Path
import json

RESULTS_DIR = Path(os.path.join(__file__, "..", "..", "results")).resolve()

# Save the dictionary as JSON as a result file
def save_result(pipeline, name, df):
    filename = os.path.join(RESULTS_DIR, pipeline + "-" + name + ".json")

    print("Exporting results:", os.path.basename(filename), end=" ... ", flush=True)

    with open(filename, "w", encoding="utf-8") as file:
        df.to_json(file, orient="records", force_ascii=False, indent=2)

    print("✅")

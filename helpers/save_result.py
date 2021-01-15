import os
from pathlib import Path
import json

RESULTS_DIR = Path(os.path.join(__file__, "..", "..", "results")).resolve()

# Save the dictionary as JSON as a result file
def save_result(pipeline, name, dict):
    filename = os.path.join(RESULTS_DIR, pipeline + "-" + name + ".json")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict, file, ensure_ascii=False, indent=2)

    print("Exported results:", os.path.basename(filename), "✅")

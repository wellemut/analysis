from database import Database, Field
import numpy as np

analysis_db = Database("analysis")

# Pass in a dataframe with a domain and the columns to update
def update_analysis_database(df):
    print("Updating domains in", f"{analysis_db.name}.sqlite", end=" ... ", flush=True)

    # Replace nan in dataset with None
    df = df.replace({np.nan: None})

    # Write data to analysis database
    with analysis_db.start_transaction() as transaction:
        for _i, row in df.iterrows():
            data = row.to_dict()
            domain = data.pop("domain")
            analysis_db.table("domains").set(**data).where(
                Field("domain") == domain
            ).execute()

    print("✅")

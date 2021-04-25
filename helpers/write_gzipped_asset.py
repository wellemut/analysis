import os
import gzip

# Write compressed asset content to the provided path
def write_gzipped_asset(path, content):
    # Create directory unless exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write asset
    with gzip.open(path, "wt") as f:
        f.write(content)

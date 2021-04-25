import gzip

# Read compressed asset content from the provided path
def read_gzipped_asset(path):
    with gzip.open(path, "rt") as f:
        return f.read()

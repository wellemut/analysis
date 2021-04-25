import os
import math
from config import HTML_FILES_DIR

# Return the HTML asset path for a given URL id
def get_html_asset_path(url_id):
    # We create subdirectories for every 10k files
    directory = str(math.floor(url_id / 10000))
    return os.path.join(HTML_FILES_DIR, directory, f"{url_id}.gz")

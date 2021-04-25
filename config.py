import os

MAIN_DATABASE = "main"

# Folder for all our database files (.sqlite)
ASSETS_DIR = os.path.join("assets")
DATABASES_DIR = os.path.join(ASSETS_DIR, "databases")
HTML_FILES_DIR = os.path.join(ASSETS_DIR, "html", MAIN_DATABASE)

# Folder for exported files
EXPORT_DIR = os.path.join("export")
EXPORT_GRAPHS_DIR = os.path.join("export", "graphs")

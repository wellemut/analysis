import os

# Folder for all our database files (.sqlite)
ASSETS_DIR = os.path.join("assets")
DATABASES_DIR = os.path.join(ASSETS_DIR, "databases")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")

# Folder for exported files
EXPORT_DIR = os.path.join("export")
EXPORT_GRAPHS_DIR = os.path.join("export", "graphs")

MAIN_DATABASE = "main"

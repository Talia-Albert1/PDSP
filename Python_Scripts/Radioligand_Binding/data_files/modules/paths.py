import os

# Directories
INPUT_DIR = "input"
ARCHIVE_DIR = "archive"
DATA_FILES_DIR = "data_files"

# Create DIR's that do not exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Radioactivity Archive Paths
RADIOACTIVITY_TEMPLATE_PATH = os.path.join(DATA_FILES_DIR, "Radioactivity_Archive_Template.xlsx")
RADIOACTIVITY_PATH = "Radioactivity_Archive.xlsx"

# User Config Path
USER_CONFIG_PATH = os.path.join(DATA_FILES_DIR, "user_config.json")

# Binding Printout Template
PRINTOUT_TEMPLATE_PATH = os.path.join(DATA_FILES_DIR, "Binding_Printout_Template.xlsx")

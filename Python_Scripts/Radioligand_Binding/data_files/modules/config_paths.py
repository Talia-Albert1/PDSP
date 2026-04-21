from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# directories
INPUT_DIR = PROJECT_ROOT / "input"
ARCHIVE_DIR = PROJECT_ROOT / "archive"
DATA_FILES_DIR = PROJECT_ROOT / "data_files"

# file paths
USER_CONFIG_PATH = DATA_FILES_DIR / "user_config.json"
RADIOACTIVITY_PATH = PROJECT_ROOT / "Radioactivity_Archive.xlsx"
RADIOACTIVITY_TEMPLATE_PATH = DATA_FILES_DIR / "Radioactivity_Archive_Template.xlsx"
PRINTOUT_TEMPLATE_PATH = DATA_FILES_DIR / "Binding_Printout_Template.xlsx"

def initialize_directories()-> None:
    """Ensures directories exist"""
    directories = [INPUT_DIR, ARCHIVE_DIR, DATA_FILES_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_daily_paths(formatted_date:str) -> dict[str, Path]:
    """Generates Dict of Paths specified to a date"""
    return {
        "barcode": INPUT_DIR / f"{formatted_date}_Barcodes.txt",
        "worklist": INPUT_DIR / f"{formatted_date}_Worklist.txt",
        "printout": ARCHIVE_DIR / f"{formatted_date} - Binding Printout.xlsx",
        "log": ARCHIVE_DIR / f"{formatted_date}_Binding_Worksheet.log"
    }

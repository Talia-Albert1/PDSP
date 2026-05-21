import logging

import pandas as pd
from pathlib import Path
import openpyxl

logger = logging.getLogger(__name__)

# column index in excel is linked to dict, where "key" is the column name
# in the dataframe
COLUMN_SCHEMA = {
    "A":  {"key": "Binding Type",             "bold": True,  "align": "left",   "border": "normal",      "green_toggle": False},
    "B":  {"key": "Plate Name",               "bold": True,  "align": "left",   "border": "normal",      "green_toggle": False},
    "C":  {"key": "Date",                     "bold": False, "align": "center", "border": "thick_right", "green_toggle": False},
    "D":  {"key": "Barcode 0",                "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    # plate_number
    "E":  {
        "key": None,                          "bold": False, "align": "center", "border": "normal",      "green_toggle": False,
        "formula": lambda r, idx, row, prev: 1 if idx == 0 else f'=IF(A{r - 1}="SEC", K{r - 1} + 1, E{r - 1} + 1)'
    },
    # submission_confirm
    "F":  {"key": None,                       "bold": False, "align": "center", "border": "normal",      "green_toggle": True},
    "G":  {"key": "Barcode 1",                "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    # plate_number
    "H":  {
        "key": None,                          "bold": False, "align": "center", "border": "normal",      "green_toggle": False,
        "formula": lambda r, idx, row, prev: f'=IF(A{r}="SEC", E{r} + 1, "")'
    },
    # submission_confirm
    "I":  {
        "key": None,                          "bold": False, "align": "center", "border": "normal",      "green_toggle": True,
        "formula": lambda r, idx, row, prev: f'=F{r}' if str(row.get("Binding Type")).lower() == "sec" else None
    },
    "J":  {"key": "Barcode 2",                "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    # plate_number
    "K":  {
        "key": None,                          "bold": False, "align": "center", "border": "normal",      "green_toggle": False,
        "formula": lambda r, idx, row, prev: f'=IF(A{r}="SEC", H{r} + 1, "")'
    },
    # submission_confirm
    "L":  {
        "key": None,                          "bold": False, "align": "center", "border": "thick_right", "green_toggle": True,
        "formula": lambda r, idx, row, prev: f'=F{r}' if str(row.get("Binding Type")).lower() == "sec" else None
    },
    # pellet_book_confirm
    "M":  {"key": None,                       "bold": False, "align": "center", "border": "normal",      "green_toggle": True},
    # ligand_book_confirm
    "N":  {"key": None,                       "bold": False, "align": "center", "border": "normal",      "green_toggle": True},
    # actual_counts
    "O":  {"key": None,                       "bold": False, "align": "center", "border": "normal",      "green_toggle": True},
    # worklist_confirmation
    "P":  {
        "key": None,                          "bold": False, "align": "center", "border": "thick_right", "green_toggle": False,
        "formula": lambda r, idx, row, prev: (
            f'=P{r - 1}' if (idx != 0 and prev and 
                             row.get("Ligand") == prev.get("Ligand") and 
                             row.get("Assay Conc") == prev.get("Assay Conc"))
            else None
        )
    },
    "Q":  {"key": "Receptor",                 "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    "R":  {"key": "Assay Conc",               "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    # actual_assay_conc
    "S":  {
        "key": None, "bold": False, "align": "center", "border": "normal", "green_toggle": False, "num_format": "0.00",
        "formula": lambda r, idx, row, prev: f'=O{r}*(1/2.22E+12)*(1/W{r})*(1/0.125)*10^9'
    },
    "T":  {"key": "Ligand",                   "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    "U":  {"key": "Radionuclide",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "V":  {"key": "Inventory Control Number", "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "W":  {"key": "Specific Activity",        "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "X":  {"key": "Initial Quantity mCi",     "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "Y":  {"key": "Initial Volume uL",        "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "Z":  {"key": "uCi/uL Ratio",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AA": {"key": "mCi Remaining",            "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AB": {"key": "uL Remaining",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AC": {"key": "Date Received",            "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AD": {"key": "Date Started",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AE": {"key": "Date Last Used",           "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AF": {"key": "Calibration Date",         "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AG": {"key": "Decay Factor",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AH": {"key": "Reference",                "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    "AI": {"key": "Number of Plates",         "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AJ": {"key": "Number of Pellets",        "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AK": {"key": "Buffer Volume",            "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AL": {"key": "uL for Assay",             "bold": False, "align": "center", "border": "normal",      "green_toggle": False, "round": 2},
    "AM": {"key": "uCi for Assay",            "bold": False, "align": "center", "border": "normal",      "green_toggle": False, "round": 2},
    "AN": {"key": "Sink Waste (uCi)",         "bold": False, "align": "center", "border": "normal",      "green_toggle": False, "round": 2},
    "AO": {"key": "Dry Waste (uCi)",          "bold": False, "align": "center", "border": "normal",      "green_toggle": False, "round": 2},
    "AP": {"key": "Assay BB",                 "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    "AQ": {"key": "Filter Type",              "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AR": {"key": "Unifilter Pellet Ratio",   "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AS": {"key": "Filtermat Pellet Ratio",   "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AT": {"key": "Pellets in Inventory",     "bold": False, "align": "center", "border": "normal",      "green_toggle": False},
    "AU": {"key": "Assay DB Notes",           "bold": False, "align": "left",   "border": "normal",      "green_toggle": False},
    "AV": {"key": "Pellet DB Notes",          "bold": False, "align": "left",   "border": "normal",      "green_toggle": False}
}

def safe_load_workbook(file_path):
    """
    Safely loads an Excel workbook, prompt-retrying if the file is locked open.
    """
    while True:
        try:
            wb = openpyxl.load_workbook(file_path)
            return wb
        except PermissionError:
            logging.warning(f"Permission Denied: The file '{file_path}' is currently open or locked.")
            print(f"\n[WARNING] Please CLOSE the Excel file: {file_path}")
            user_input = input("Once closed, press [Enter] (or type 'y' and press Enter) to retry: ")
            # Optional check if you explicitly want 'y', though any key/Enter is usually more user-friendly
            time.sleep(0.5)  # Tiny buffer to let OS release file lock
        except Exception as e:
            logging.error(f"Failed to load workbook due to an unexpected error: {e}")
            raise e



def safe_save_workbook(wb, file_path):
    """
    Safely saves an Excel workbook, prompt-retrying if the file is locked open.
    """
    while True:
        try:
            wb.save(file_path)
            logging.info(f"Workbook successfully saved to {file_path}")
            return True
        except PermissionError:
            logging.warning(f"Permission Denied: Cannot save. The file '{file_path}' is currently open.")
            print(f"\n[WARNING] CRITICAL: Cannot save changes! The file is open: {file_path}")
            user_input = input("Please CLOSE the file in Excel, then press [Enter] to retry saving: ")
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"Failed to save workbook due to an unexpected error: {e}")
            raise e



def write_archive_excel(
        archive_sheet_path: Path,
        df                : pd.DataFrame,
        column_schema     : dict[str, dict],
        gray_switch       :
):
    wb = safe_load_workbook(archive_sheet_path)
    ws = wb['Sheet1']
    last_row = ws.max_row

    if gray_switch == '0':
        gray_switch = '1'
        cell_fill_color = 'D9D9D9'#Gray
    elif gray_switch == '1':
        gray_switch = '0'
        cell_fill_color = 'FFFFFF'#White


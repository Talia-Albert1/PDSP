import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe
import time
import logging
logger = logging.getLogger(__name__)
# Define the scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]

# Google Sheet Names
GSHEET_FILE_NAME = 'PDSP'
GSHEET_CONFIG = {
    "Assay_DB": {
        "sheet_name": "Assay_Param",
        "type":       "database",
        "schema": {
            "Receptor":                     {"column_name": "Receptor",                     "format": str},
            "Ligand":                       {"column_name": "Ligand",                       "format": str},
            "Assay Conc":                   {"column_name": "Assay Conc. (nM)",             "format": float},
            "PRIM Pellet Ratio":            {"column_name": "PRIM Pellet/Plate Ratio",      "format": float},
            "SEC Pellet Ratio":             {"column_name": "SEC Pellet/Plate Ratio",       "format": float},
            "Assay BB":                     {"column_name": "Assay BB",                     "format": str},
            "Reference":                    {"column_name": "Reference",                    "format": str},
            "Filter Type":                  {"column_name": "Filter Type?",                 "format": str},
            "Unifilter Pellet Ratio":       {"column_name": "Unifilter Pellet/Plate Ratio", "format": float},
            "Filtermat Pellet Ratio":       {"column_name": "Filtermat Pellet/Plate Ratio", "format": float},
            "Notes":                        {"column_name": "Notes",                        "format": str},
        },
    },
    "Ligand_DB": {
        "sheet_name": "Hotligand_Inventory",
        "type":       "database",
        "schema": {
            "Ligand":                      {"column_name": "Ligand",                      "format": str},
            "Radionuclide":                {"column_name": "Radionuclide",                "format": str},
            "Inventory Control Number":    {"column_name": "Inventory Control Number",    "format": str},
            "Specific Activity":           {"column_name": "Specific Activity (Ci/mmol)", "format": float},
            "Initial Quantity mCi":        {"column_name": "Quantity (mCi)",              "format": float},
            "Initial Volume uL":           {"column_name": "Volume (uL)",                 "format": float},
            "uCi/uL Ratio":                {"column_name": "uCi/uL Ratio",                "format": float},
            "mCi Remaining":               {"column_name": "Quantity Remaining (mCi)",    "format": float},
            "uL Remaining":                {"column_name": "Volume Remaining (uL)",       "format": float},
            "Date Received":               {"column_name": "Date Received",               "format": "datetime64[ns]"},
            "Date Started":                {"column_name": "Date Started",                "format": "datetime64[ns]"},
            "Date Last Used":              {"column_name": "Date Last Used",              "format": "datetime64[ns]"},
            "Current Vial":                {"column_name": "Current Vial?",               "format": bool},
            "Finished":                    {"column_name": "Finished?",                   "format": bool},
            "Calibration Date":            {"column_name": "Calibration Date",            "format": "datetime64[ns]"},
        },
    },
    "Pellet_DB": {
        "sheet_name": "Pellet_Inventory",
        "type":       "database",
        "schema": {
            "Receptor":          {"column_name": "Receptor",          "format": str},
            "Number of Pellets": {"column_name": "Number of Pellets", "format": float},
            "Notes":             {"column_name": "Notes",             "format": str},
        },
    },
    "Hotligand_Log": {
        "sheet_name": "Hotligand_log",
        "type":       "log",
    },
    "Pellet_Log": {
        "sheet_name": "Pellet_Log",
        "type":       "log",
    },
}

def gsheet_api_call(func, *args, max_retries=3, **kwargs):
    """small gshet api call wrapper for better error handling"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 429:  # Rate limit
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                logger.warning(f'Google Sheets rate limit hit, retrying in {wait}s (attempt {attempt + 1}/{max_retries})')
                time.sleep(wait)
            else:
                logger.error(f'Google Sheets API error: {e}')
                raise
        except Exception as e:
            logger.error(f'Unexpected error during Google Sheets call: {e}')
            raise
    logger.error(f'Google Sheets API call failed after {max_retries} attempts')
    raise RuntimeError('Max retries exceeded for Google Sheets API call')





def load_gsheet_db(gsheet_file, gsheet_sheet_name:str)->pd.DataFrame:
    """read in an individual sheet

    Args:
        gsheet_file_name (str): The name of the Google Sheets File
        gsheet_sheet_name (str): The name of the Sheet within the Google Sheets File

    Returns:
        pd.DataFrame: DataFrame of Sheet
    """
    
    indv_sheet = gsheet_api_call(gsheet_file.worksheet, gsheet_sheet_name)
    df = gsheet_api_call(
        get_as_dataframe,
        indv_sheet,
        value_render_option='FORMATTED_VALUE',
        evaluate_formulas=True
        )
    

    # drop empty/trailing rows
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)

    # log sheet shape
    logger.info(f"Google sheet accessed: {gsheet_sheet_name}")
    logger.info(f"{gsheet_sheet_name} Shape: {df.shape}")
    logger.info(f"{gsheet_sheet_name} Columns:\n{df.columns}")
    logger.info(f"{gsheet_sheet_name} First 5 Rows:\n{df.head()}")

    return df






def load_all_gsheet_db(client, gsheet_file_name:str, gsheet_config:dict[str, dict])->dict[str, pd.DataFrame]:
    gsheet_file = client.open(gsheet_file_name)
    database_df = {}
    for internal_id, config in gsheet_config.items():
        if config['type'] == "database":
            sheet_name = config['sheet_name']
            df = load_gsheet_db(gsheet_file, sheet_name)
            database_df[internal_id] = df
            logger.info(f"Loaded Database: '{internal_id}' from Google Sheet: '{config['sheet_name']}'")
        
    return database_df


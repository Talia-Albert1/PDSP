import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe
import time
import logging
logger = logging.getLogger(__name__)
# Define the scope
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Google Sheet Names
GSHEET_FILE_NAME = 'PDSP'
GSHEET_DB_NAMES = {
    "Assay_DB" : 'Assay_Param',
    "Ligand_DB": 'Hotligand_Inventory',
    "Pellet_DB": 'Pellet_Inventory'
}
GSHEET_LOG_NAMES ={
    "Hotligand_Log": "Hotligand_Log",
    "Pellet_Log"   : "Pellet_Log"
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
        client (_type_): _description_
        gsheet_file_name (str): _description_
        gsheet_sheet_name (str): _description_

    Returns:
        pd.DataFrame: _description_
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

def load_all_gsheet_db(client, gsheet_file_name:str, gsheet_db_names:dict[str, str])->dict[str, pd.DataFrame]:
    gsheet_file = client.open(gsheet_file_name)
    database_df = {}
    for db_type, sheet_name in gsheet_db_names.items():
        df = load_gsheet_db(gsheet_file, sheet_name)
        database_df[db_type] = df
        logger.info(f"Loaded Database: '{db_type}' from Google Sheet: '{sheet_name}'")
    
    return database_df


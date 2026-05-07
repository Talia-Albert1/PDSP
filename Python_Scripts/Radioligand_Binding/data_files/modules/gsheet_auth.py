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
GSHEET_CONFIG = {
    "Assay_DB": {
        "sheet_name":"Assay_Param",
        "type"      :"database",
        "schema":{
            'Receptor'                    :str,
            'Ligand'                      :str,
            'Radionuclide'                :str,
            'Assay Conc. (nM)'            :float,
            'PRIM Pellet/Plate Ratio'     :float,
            'SEC Pellet/Plate Ratio'      :float,
            'Assay BB'                    :str,
            'Reference'                   :str,
            'Filter Type?'                :str,
            'Unifilter Pellet/Plate Ratio':float,
            'Filtermat Pellet/Plate Ratio':float,
            'Notes'                       :str
        },
    },
    "Ligand_DB":{
        "sheet_name":"Hotligand_Inventory",
        "type"      :"database",
        "schema":{
            'Ligand'                     :str,
            'Radionuclide'               :str,
            'Inventory Control Number'   :str,
            'Specific Activity (Ci/mmol)':float,
            'Quantity (mCi)'             :float,
            'Volume (uL)'                :float,
            'uCi/uL Ratio'               :float,
            'Quantity Remaining (mCi)'   :float,
            'Volume Remaining (uL)'      :float,
            'Date Received'              :'datetime64[ns]',
            'Date Started'               :'datetime64[ns]',
            'Date Last Used'             :'datetime64[ns]',
            'Current Vial?'              :bool,
            'Finished?'                  :bool,
            'Calibration Date'           :'datetime64[ns]'
        },
    },
    "Pellet_DB":{
        "sheet_name":"Pellet_Inventory",
        "type"      :"database",
        "schema":{
            'Receptor'         :str,
            'Number of Pellets':float,
            'Notes'            :str
        },
    },
    "Hotligand_Log":{
        'sheet_name':'Hotligand_log',
        'type'      :'log'
    },
    "Pellet_Log":{
        'sheet_name':'Pellet_Log',
        'type'      :'log'
    }
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


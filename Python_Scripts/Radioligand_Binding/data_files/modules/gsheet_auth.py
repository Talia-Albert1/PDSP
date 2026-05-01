import gspread
import time
import logging
logger = logging.getLogger(__name__)
# Define the scope
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

# Google Sheet Names
GSHEET_NAME = 'PDSP'
GSHEET_SHEET_ASSAY_DB_NAME = 'Assay_Param'
GSHEET_SHEET_LIGAND_DB_NAME = 'Hotligand_Inventory'
GSHEET_SHEET_ASSAY_DB_NAME = 'Pellet_Inventory'

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


import logging

import pandas as pd
logger = logging.getLogger(__name__)


def merge_intial_inputs(barcode_raw:list[str], worklist_raw:list[str]) -> pd.DataFrame:
    """Takes the raw list of barcodes and raw list of text files and merges them into
    a single dataframe.

    Args:
        barcode_raw (list[str]): list of barcode strings
        worklist_raw (list[str]): list of worklist line strings (should be tab separated)

    Returns:
        pd.DataFrame: Merged dataframe of Platenames, Receptors, and Barcodes
    """
    # --------------------------------------------------------------------------------
    # CREATE LIST OF DICTS
    # --------------------------------------------------------------------------------
    # Duplicate list which will get popped later
    barcodes = barcode_raw.copy()

    # Receptor, Binding Type, Barcode 0, Barcode 1, Barcode 2
    intial_input = []
    for entry in worklist_raw:
        columns = entry.split('\t')
        binding_type = columns[0].upper().strip()
        plate_name = columns[1]

        # PRIM = 1 Barcode
        # SEC  = 3 Barcodes
        if binding_type == "PRIM":
            barcode_0 = barcodes.pop(0)
            barcode_1 = None
            barcode_2 = None
        
        elif binding_type == "SEC":
            barcode_0 = barcodes.pop(0)
            barcode_1 = barcodes.pop(0)
            barcode_2 = barcodes.pop(0)
        
        intial_input.append({
            "Plate Name"  : plate_name,
            "Binding Type": binding_type,
            "Barcode 0"   : barcode_0,
            "Barcode 1"   : barcode_1,
            "Barcode 2"   : barcode_2
        })
    logger.info(f"Text files loaded into List of Dicts with {len(intial_input)} rows")
    # --------------------------------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------------------------------
    df = pd.DataFrame(intial_input)

    # --------------------------------------------------------------------------------
    # DETERMINE RECEPTOR NAME FROM PLATE NAME
    # --------------------------------------------------------------------------------
    # use regex to identify receptor name
    # all plates will end in "-0", "-1", ... "-99"
    # limiting to 2 digits to keep specificity, do not want to accidentally remove receptor names
    # "5-HT1A" for example
    pattern = r'-\d{1,2}$'
    df['Receptor'] = df['Plate Name'].str.replace(pattern, '', regex=True)
    logger.info(f"Receptor Names Determined from Plate Names")

    # check that the regex was successful
    # it does not necessairly need to match, if it's entered without a plate name
    failed_mask = df['Receptor'] == df['Plate Name']
    failed_matches = df.loc[failed_mask, 'Receptor'].unique().tolist()
    if failed_matches:
        logger.warning(
            f"Regex failed to trim plate names for:{failed_matches}, "
            "may result in error when matching receptors"
            )
        logger.warning("Plate names should end in '-XX' and can only be 2 digits max")



    # --------------------------------------------------------------------------------
    # LOG SHAPE
    # --------------------------------------------------------------------------------
    logger.info(f"Shape of Created DataFrame: {df.shape}")
    logger.info(f"Dataframe Columns:\n{df.columns}")
    logger.info(f"First 5 Rows of User Input DataFrame:\n{df.head()}")
    return df

import logging

import pandas as pd
logger = logging.getLogger(__name__)

def determine_receptor(plate_name:str) -> str:
    
    return

def merge_intial_inputs(barcode_raw:list[str], worklist_raw:list[str]) -> pd.DataFrame:
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
    logger.info(f"Dataframe Columns: {df.columns}")
    logger.info(f"\n{df.head()}")
    logger.info(f"Shape of Created DataFrame: {df.shape}")

    return df

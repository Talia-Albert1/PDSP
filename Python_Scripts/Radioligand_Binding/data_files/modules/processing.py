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
    df['Receptor'] = df['Plate Name'].str.replace(pattern, '', regex=True).str.replace(" ","", regex=False)
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


def format_gsheet_dfs(gsheet_database_dfs:dict[str,pd.DataFrame], gsheet_config:dict[str,dict])->dict[str,dict]:
    database_dict = {}
    for db_type, df in gsheet_database_dfs.items():
        for col in df:
            if col not in gsheet_config[db_type]['schema'].keys():
                logger.warning(f"{col} not formatted, not in GSHEET_CONFIG: {gsheet_config[db_type]['schema'].keys()}")
                continue
            format = gsheet_config[db_type]['schema'][col]
            df[col] =  df[col].astype(format)
        database_dict[db_type] = df
        logger.info(f"{db_type} DataFrame columns formatted")
    return database_dict

def format_gsheet_dfs(gsheet_database_dfs: dict[str, pd.DataFrame], gsheet_config: dict[str, dict]) -> dict[str, pd.DataFrame]:
    """Format the google sheet dataframes to ensure columns are the correct type.
    Also renames columns to internal name.

    Args:
        gsheet_database_dfs (dict[str, pd.DataFrame]): dictionary of dataframes, where the keys are internal names
        gsheet_config (dict[str, dict]): config constant for google sheet data

    Returns:
        dict[str, pd.DataFrame]: dictonary of formatted dataframes.
    """
    database_dict = {}
    
    for db_type, df in gsheet_database_dfs.items():
        # Skip if the sheet type is a log or not in config
        if db_type not in gsheet_config or gsheet_config[db_type].get('type') != 'database':
            database_dict[db_type] = df
            continue

        schema_info = gsheet_config[db_type].get('schema', {})
        
        # Mapping: {GSheet Column Name: Internal Key}
        rename_map = {details['column_name']: internal_name for internal_name, details in schema_info.items()}
        # Mapping: {GSheet Column Name: Column Format}
        format_map = {details['column_name']: details['format'] for internal_name, details in schema_info.items()}

        current_df_cols = df.columns.tolist()
        
        for col in current_df_cols:
            if col not in rename_map:
                logger.warning(f"Column '{col}' not in GSHEET_CONFIG for {db_type}. Skipping.")
                continue
            
            # Apply formatting
            target_format = format_map[col]
            try:
                df[col] = df[col].astype(target_format)
            except Exception as e:
                logger.error(f"Error casting {db_type} column '{col}' to {target_format}: {e}")

        # Rename to internal keys and filter to only include columns defined in schema
        df = df.rename(columns=rename_map)
        internal_names = list(schema_info.keys())
        
        # Final DataFrame contains only the renamed, formatted columns
        database_dict[db_type] = df[df.columns.intersection(internal_names)]
        
        logger.info(f"Successfully formatted and renamed {db_type} DataFrame")
        
    return database_dict

def merge_dfs(input_df:pd.DataFrame, gsheet_database_dfs:dict[str,pd.DataFrame])->pd.DataFrame:
    
    # --------------------------------------------------------------------------------
    # MERGE ASSAY PARAMS WITH INPUT
    # --------------------------------------------------------------------------------
    logger.info("Merging input df with assay db")
    # Merge input df and assay_db df on receptor, left join preserves input df
    df_merged_assay = input_df.merge(
        gsheet_database_dfs["Assay_DB"],
        on = "Receptor",
        how = "left",
        indicator=True,
        validate="m:1"
    )

    # Filter for rows that only exist in the left (input) dataframe
    unmatched = df_merged_assay[df_merged_assay["_merge"] == "left_only"]
    unmatched_count = len(unmatched)

    if unmatched_count > 0:
        # Get the specific receptors that failed so the user can fix the Google Sheet or input
        # create df that informs user on specific unmatched plates
        error_df = unmatched.loc[:, ["Plate Name", "Binding Type", "Receptor"]]
        failed_receptors = unmatched["Receptor"].unique().tolist()
        msg = (
            f"{unmatched_count} rows unmatched. "
            f"Plates not matched: {error_df}"
            f"\nReceptors not found in Assay_DB: {failed_receptors}"
        )
        logger.warning(msg)
        raise ValueError(msg)
    else:
        logger.info("All Assay Condition rows matched successfully.")
    df_merged_assay = df_merged_assay.drop(columns=["_merge"])

    # --------------------------------------------------------------------------------
    # FILTER HOTS DF FOR ONLY CURRENT VIALS
    # --------------------------------------------------------------------------------    
    df_hot_current = gsheet_database_dfs["Ligand_DB"]
    # Keep only rows with True current vial and where ligand is not Na
    df_hot_current = df_hot_current[df_hot_current["Current Vial"] == True & df_hot_current["Ligand"].notna()]

    # --------------------------------------------------------------------------------
    # MERGE HOTLIGAND INFO WITH INPUT
    # --------------------------------------------------------------------------------
    df_merged = df_merged_assay.merge(
        df_hot_current,
        on="Ligand",
        how="left",
        indicator=True,
        validate="m:1"
    )

    # Filter for rows that only exist in the left (input) dataframe
    unmatched = df_merged[df_merged["_merge"] == "left_only"]
    unmatched_count = len(unmatched)

    if unmatched_count > 0:
        # Get the specific receptors that failed so the user can fix the Google Sheet or input
        # create df that informs user on specific unmatched plates
        error_df = unmatched.loc[:, ["Ligand"]]
        failed_ligands = unmatched["Ligand"].unique().tolist()
        msg = (
            f"{unmatched_count} rows unmatched. "
            f"Ligands not found in Ligands_DB: {failed_ligands} "
            f"Ensure ligands are marked as 'True' under 'Current Vial?' on the Google Sheet"
        )
        logger.warning(msg)
        raise ValueError(msg)
    else:
        logger.info("All Ligand rows matched successfully.")

    df_merged = df_merged.drop(columns=["_merge"])
    return df_merged

def calc_material_usage(merged_df:pd.DataFrame)->pd.DataFrame:
    def calculate_radioactive_material(
            buffer_vol       :int,
            assay_conc       :float,
            specific_activity:float,
            dilution_factor  :float = 2.5,
            overage_percent  :float = 1.44,
            uci_ul_ratio     :float
            ) -> float:
        uci_amount = buffer_vol * assay_conc * specific_activity * (1/1000) * dilution_factor * overage_percent
        ul_amount = uci_amount * uci_ul_ratio

        return uci_amount,ul_amount
    


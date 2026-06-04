import logging

import pandas as pd
import numpy as np
import datetime

from pathlib import Path
import shutil
logger = logging.getLogger(__name__)

# NOTE: Some receptor names need to be harcoded to map, the worklist tool
# NOTE: prints "BZP Rat Brain Site-X" the way the receptor named is determined
# NOTE: needs hard coded options to detect that "BZP Rat Brain Site-X" is "BZP-X"
# NOTE: "Str of receptor we look for":"receptor name we want"
# NOTE: If we find the string "BZP" in any way in the receptor name, the name becomes BZP
RECEPTOR_MAPPING = {
    "BZP" : "BZP"
}

def merge_intial_inputs(
    barcode_raw:list[str],
    worklist_raw:list[str],
    receptor_mapping:dict[str,str]
)->pd.DataFrame:
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
    
    # cycle through & replace hard coded names first
    for keyword, clean_name in receptor_mapping.items():
        spaced_keyword_pattern = " *".join(list(keyword))
        
        # Check if the keyword exists (ignoring case)
        mask = df["Receptor"].str.contains(spaced_keyword_pattern, case=False, na=False)
        
        # Wherever it matches, overwrite that row with the clean name + the original suffix
        df.loc[mask, "Receptor"] = clean_name

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
                logger.warning(f"Column '{col}' in Google Sheets, not in GSHEET_CONFIG for {db_type}. Skipping.")
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
    logger.info("Merging input DataFrame with Assay_DB")
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
    logger.info("Filtering Ligand_DB to only have Current Vials")
    
    df_hot_current = gsheet_database_dfs["Ligand_DB"]
    # Keep only rows with True current vial and where ligand is not Na
    df_hot_current = df_hot_current[df_hot_current["Current Vial"] == True & df_hot_current["Ligand"].notna()]

    # --------------------------------------------------------------------------------
    # MERGE HOTLIGAND INFO WITH INPUT
    # --------------------------------------------------------------------------------
    logger.info("Merging Hot Ligand (Ligand_DB) with Merged DataFrame")
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

    # --------------------------------------------------------------------------------
    # MERGE PELLET INVENTORY INFO WITH INPUT
    # --------------------------------------------------------------------------------
    logger.info("Merging Pellet Inventory (Pellet_DB) with Merged DataFrame")
    df_merged = df_merged.merge(
        gsheet_database_dfs["Pellet_DB"],
        left_on="Pellet Used",
        right_on="Receptor",
        how="left",
        indicator=True,
        validate="m:1",
        suffixes=("", "_drop")
    )

    # Safely drop the duplicate column from the database
    df_merged = df_merged.drop(columns=["Receptor_drop"])
    
    # Filter for rows that only exist in the left (input) dataframe
    unmatched = df_merged[df_merged["_merge"] == "left_only"]
    unmatched_count = len(unmatched)
    
    if unmatched_count > 0:
        # Get the specific receptors that failed so the user can fix the Google Sheet or input
        # create df that informs user on specific unmatched plates
        error_df = unmatched.loc[:, ["Receptor"]]
        failed_receptors = unmatched["Receptor"].unique().tolist()
        msg = (
            f"{unmatched_count} rows unmatched. "
            f"Receptors not found in Pellet_DB: {failed_receptors} "
            f"Ensure Receptor name is in the Pellet_DB Google Sheet"
        )
        # don't raise error, script can proceed without inventory
        logger.warning(msg)

    else:
        logger.info("All Pellet Inventory rows matched successfully.")

    df_merged = df_merged.drop(columns=["_merge"])

    
    # log df shape -------------------------------------------------------------------
    logger.info(f"Merged DataFrame Shape: {df_merged.shape}")
    logger.info(f"Merged DataFrame Columns:\n{df_merged.columns}")
    logger.info(f"Merged DataFrame First 5 Rows:\n{df_merged.head()}")
    return df_merged



def calc_material_usage(now:datetime, df:pd.DataFrame)->pd.DataFrame:
    # ==============================================================================
    # ADD TODAY'S DATE
    # ==============================================================================
    df["Date"] = pd.to_datetime(now)

    # ==============================================================================
    # DETERMINE BUFFER VOLUME & NUMBER OF PLATES
    # ==============================================================================
    logger.info("Determining Buffer Volume & Number of Plates")

    binding_conditions = [
        (df["Binding Type"] == "PRIM"),
        (df["Binding Type"] == "SEC")
    ]

    # PRIM = 1 Plate  = 5  mL Buffer
    # SEC  = 3 Plates = 15 mL Buffer
    df["Number of Plates"] = np.select(binding_conditions, [1, 3], default=1)
    df["Buffer Volume (mL)"] = np.select(binding_conditions, [5, 15], default=5)
    logger.info("Buffer Volumes & Number of Plates Calculated")
    # ==============================================================================
    # CALCULATE RAD MATERIAL USAGE
    # ==============================================================================
    logger.info("Calculating Radioactive Material Usage")

    # calculate uci needed for assay -----------------------------------------------
    dilution_factor = 2.5
    overage_percent = 1.44 #1.2 * 1.2
    df["uCi for Assay"] = df["Buffer Volume (mL)"] * df["Assay Conc"] * df["Specific Activity"] * (1/1000) * dilution_factor * overage_percent
    logger.info("uCi per Assay calculated")
    
    # calculate sink & dry waste for individual assay ------------------------------
    # NOTE: these rounded numbers are only used if we need to back calculate
    # NOTE: the numbers used for the actual log are generated in a summary section
    df["Sink Waste (uCi)"] = df["uCi for Assay"] * 0.8
    df["Dry Waste (uCi)"]  = df["uCi for Assay"] * 0.2

    # calculate decay factor for I125, for H3 it is 1 ------------------------------
    # np.log is base e (effectively this is ln(2))
    day_since_cal = (df["Date"] - df["Calibration Date"]).dt.days
    I125_decay_factor = np.exp((-np.log(2)/60.1)*day_since_cal)
    
    decay_factor_conditions = [(df["Radionuclide"] == "H3"), (df["Radionuclide"] == "I125")]
    decay_factor_choices = [1, I125_decay_factor]
    df["Decay Factor"] = np.select(decay_factor_conditions, decay_factor_choices, default=1.0)

    # calculate uL needed for assay ------------------------------------------------
    df["uL for Assay"] = df["uCi for Assay"] / (df["uCi/uL Ratio"] * df["Decay Factor"])
    logger.info("uL per Assay calculated")

    # ==============================================================================
    # CALCULATE PELLET USAGE
    # ==============================================================================
    logger.info("Calculating Pellet Usage")

    # select which pellet ratio to use depending on filter type --------------------
    pellet_conditions = [
        (df["Filter Type"] == "Filtermat"),
        (df["Filter Type"] == "Unifilter")
    ]

    pellet_choices = [
        (df["Number of Plates"] * df["Filtermat Pellet Ratio"]),
        (df["Number of Plates"] * df["Unifilter Pellet Ratio"])
    ]

    df["Number of Pellets"] = np.select(pellet_conditions, pellet_choices, default=1)

    logger.info("Number of Pellets per Assay calculated")

    return df



def aggregate_df(df:pd.DataFrame, user_initals:str, user_name:str)->dict[str, pd.DataFrame]:
    # ==============================================================================
    # SUM BASED ON ASSAY (INCLUDING PELLET INVENTORY)
    # ==============================================================================
    logger.info("Aggregating Receptor/Assay Information")
    assay_summary = (
        df.groupby("Receptor", sort=False)
        .agg(**{
            "Date"               :("Date",                 "first"),
            "Ligand"             :("Ligand",               "first"),
            "Buffer"             :("Assay BB",             "first"),
            "Buffer Vol (mL)"    :("Buffer Volume (mL)",   "sum"),
            "Ligand Vol (uL)"    :("uL for Assay",         "sum"),
            "# of Plates"        :("Number of Plates",     "sum"),
            "# of Pellets"       :("Number of Pellets",    "sum"),
            "Reference"          :("Reference",            "first"),
            "Assay Conc. (nM)"   :("Assay Conc",           "first"),
            "Filter Type"        :("Filter Type",          "first"),
            "# Pellets Inventory":("Pellets in Inventory", "first"),
            "Pellet Used"        :("Pellet Used",          "first")
        }).reset_index()
    )

    # ==============================================================================
    # SUM BASED ON HOT LIGAND
    # ==============================================================================
    logger.info("Aggregating Hot Ligand Information")
    hotligand_summary = (
        df.groupby("Ligand")
        .agg(**{
            "Date"                    :("Date",                    "first"),
            "Radionuclide"            :("Radionuclide",            "first"),
            "Inventory Control Number":("Inventory Control Number","first"),
            "Specific Activity"       :("Specific Activity",       "first"),
            "Ligand Vol (uL)"         :("uL for Assay",            "sum"),
            "Ligand Used (uCi)"       :("uCi for Assay",           "sum"),
            "Ligand in Vial (mCi)"    :("mCi Remaining",           "first")
        })
        .reset_index()
        .sort_values(by="Ligand", ascending=True)
    )

    # ==============================================================================
    # CALCULATE RADIOACTIVE WASTE DATA
    # ==============================================================================
    # calculate waste information --------------------------------------------------
    # sink waste = 80% of Ligand Used
    # dry waste = 20% of Ligand Used
    logger.info("Calculating Rad Waste Information")
    hotligand_summary["Ligand Used (mCi)"] = np.ceil(hotligand_summary["Ligand Used (uCi)"]) / 1000
    
    # NOTE: for record keeping purposes, we cannot use more hot than what is listed.
    # NOTE: in the vial and on the sign out sheet from EHS. So if we "finish" the vial, but
    # NOTE: there is still some hot left in the vial, we treat it is "unused"
    # NOTE: We cannot use more ligand than what is left in the vial.
    # NOTE: the following calculation will change the amount of ligand used, if it
    # NOTE: would use all the hot, to just use the amount left in the vial.
    # NOTE: Example, we would use 0.025 mCi but there is only 0.015 mCi left in the
    # NOTE: vial, we will change the amount used (for record keeping only) to 0.015 mCi,
    # NOTE: since we cannot pull out more mCi from the vial than what is explicitly listed.
    # NOTE: Sorry this is so verbose, I don't have time to make it concise :)

    # ligand remaining in vial -----------------------------------------------------
    logger.info("Calculating Ligand Remaining in Vial")
    hotligand_summary["Ligand Remaining in Vial (mCi)"] = hotligand_summary["Ligand in Vial (mCi)"] - hotligand_summary["Ligand Used (mCi)"]

    # ligand remaining cannot be < 0
    logger.info("Calculating if any Vials will be finished")
    remaining_ligand_mask = hotligand_summary["Ligand Remaining in Vial (mCi)"] <= 0
    # if ligand remaining is < 0, change ligand remaining to be 0
    # if ligand remaining is < 0, change ligand used to be ligand left in vial
    hotligand_summary.loc[remaining_ligand_mask, "Ligand Remaining in Vial (mCi)"] = 0
    logger.info("If vials are finished, changing Ligand Used to be mCi in Vial")
    hotligand_summary.loc[remaining_ligand_mask, "Ligand Used (mCi)"] = hotligand_summary.loc[remaining_ligand_mask, "Ligand in Vial (mCi)"]

    # finish vial bool -------------------------------------------------------------
    logger.info("Determining if Vials are finished")
    hotligand_summary["Finishing Vial?"] = remaining_ligand_mask

    # minimum ligand usage is 0.002 mCi --------------------------------------------
    # will get overwritten later if vial was empty at time of running script
    waste_mask = hotligand_summary["Ligand Used (mCi)"] < 0.002
    hotligand_summary.loc[waste_mask, "Ligand Used (mCi)"] = 0.002

    # dry waste (20%) --------------------------------------------------------------
    logger.info("Calculating Dry Waste")
    hotligand_summary["Dry Waste"] = np.round(hotligand_summary["Ligand Used (mCi)"] * 0.2, decimals=3)

    # minimum dry waste is 0.001 mCi -----------------------------------------------
    dry_waste_mask = hotligand_summary["Dry Waste"] < 0.001
    hotligand_summary.loc[dry_waste_mask, "Dry Waste"] = 0.001
    
    # sink waste (80%) -------------------------------------------------------------
    logger.info("Calculating Sink Waste")
    hotligand_summary["Sink Waste"] = hotligand_summary["Ligand Used (mCi)"] - hotligand_summary["Dry Waste"]

    # NOTE: if there is no ligand remaining at time of running script, all waste = 0 -----
    ligand_in_vial_mask = hotligand_summary["Ligand in Vial (mCi)"] <= 0
    hotligand_summary.loc[ligand_in_vial_mask, "Ligand Used (mCi)"] = 0
    hotligand_summary.loc[ligand_in_vial_mask, "Dry Waste"] = 0
    hotligand_summary.loc[ligand_in_vial_mask, "Sink Waste"] = 0

    # ==============================================================================
    # CREATE ASSAY LIST DF
    # ==============================================================================
    logger.info("Create Assay List DF")
    # NOTE: melt converts a wide dataframe to a long dataframe
    # adding index values to ensure order later works
    df['original_row'] = df.index

    # create melted dataframe, (which will be sorted by all barcode 0, 1 then 2)
    # we use original row to then sort everything in the order we expect
    assay_list_df = df.melt(
        id_vars=['original_row', 'Plate Name', 'Binding Type'],
        value_vars=['Barcode 0', 'Barcode 1', 'Barcode 2'],
        value_name='Barcode'
    )

    # drop Na barcodes (aka PRIM plates without a Barcode 1 or Barcode 2)
    assay_list_df = assay_list_df.dropna(subset=["Barcode"])
    # remap PRIM/SEC to P/S
    assay_list_df["Binding Type"] = assay_list_df['Binding Type'].map({'PRIM': 'P', 'SEC': 'S'})

    # sort by the original row sequence to restore the user's order
    assay_list_df = assay_list_df.sort_values(by='original_row').reset_index(drop=True)

    # drop the temporary tracking column so your final output is perfectly clean
    # variable gets created from melt, to show which column the row was from
    assay_list_df = assay_list_df.drop(columns=['original_row', 'variable'])

    # ==============================================================================
    # CREATE PELLET LOG DF
    # ==============================================================================
    logger.info("Creating Pellet Log DF")
    # pellet log tracks date, receptor, initals, and quantity used -----------------
    pellet_log_cols = ["Date", "Pellet Used", "# of Pellets"]
    pellet_log_df = assay_summary[pellet_log_cols].copy()
    pellet_log_df.insert(2, "Initals", user_initals, allow_duplicates=False)
    # number of pellets used starts as positive, want to be -ve
    pellet_log_df["# of Pellets"] = pellet_log_df["# of Pellets"] * -1

    # format date column to MM/DD/YYYY
    pellet_log_df["Date"] = pellet_log_df["Date"].dt.strftime('%m/%d/%Y')

    # ==============================================================================
    # CREATE HOTLIGAND LOG DF
    # ==============================================================================
    logger.info("Creating Hotligand Log DF")
    # hotligand log tracks:
    # date, ligand, radionuclide, inventory control number, mCi used, sink, dry, name
    hotligand_log_cols = [
        "Date", "Ligand", "Radionuclide", "Inventory Control Number",
        "Ligand Used (mCi)", "Sink Waste", "Dry Waste"               
        ]
    hotligand_log_df = hotligand_summary[hotligand_log_cols].copy()
    hotligand_log_df["Name"] = user_name
        # format date column to MM/DD/YYYY
    hotligand_log_df["Date"] = hotligand_log_df["Date"].dt.strftime('%m/%d/%Y')

    # ==============================================================================
    # CREATE SUMMARY DICT TO RETURN
    # ==============================================================================
    summary_df = {
        "Assay Summary"     : assay_summary,
        "Hot Ligand Summary": hotligand_summary,
        "Assay List"        : assay_list_df
    }

    log_df = {
        "Hotligand_Log":hotligand_log_df,
        "Pellet_Log"   :pellet_log_df
    }

    # combine the dicts for printing the summary
    all_df = summary_df | log_df
    # ==============================================================================
    # PRINT SHAPES/COLUMNS OF DF
    # ==============================================================================
    for df_type, df in all_df.items():
        logger.info(f"Printing {df_type} Summary:")
        logger.info(f"{df_type} Shape: {df.shape}")
        logger.info(f"{df_type} Columns:\n{df.columns}")
        logger.info(f"{df_type} First 5 Rows:\n{df.head()}")
    
    return summary_df, log_df


def get_unique_path(target_path: Path) -> Path:
    """Checks if a file exists and appends _1, _2, etc. to make it unique."""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    directory = target_path.parent
    
    counter = 1
    while True:
        new_path = directory / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def move_input_files(daily_paths:dict[str, Path], dest_dir:Path):
    for input_file in ["barcode", "worklist"]:
        full_source_path = Path(daily_paths[input_file])
        logger.info(f"Attempting to move {full_source_path} to {dest_dir}")
        file_name = full_source_path.name
        desired_target = Path(dest_dir) / file_name
        safe_target = get_unique_path(desired_target)
        shutil.move(str(full_source_path), safe_target)
        logger.info(f"Successfully Moved {full_source_path} to {safe_target}")

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 14:43:49 2023

@author: TaliaAlbert
"""
# =============================================================================
# ############################## IMPORT MODULES ###############################
# =============================================================================
import logging
import sys
import tempfile
from pathlib import Path
import shutil

# import sub-modules ----------------------------------------------------------
from data_files.modules import config_paths as paths
from data_files.modules import config_log
from data_files.modules.time_utils import(NOW, FORMATTED_DATE)
from data_files.modules import inputs
from data_files.modules import validators
from data_files.modules import processing
from data_files.modules import gsheet_auth
from data_files.modules import excel_writer

# google sheet authentication modules -----------------------------------------
import gspread
from google.oauth2.service_account import Credentials

def main():
    # ==============================================================================
    # ################################# INITALIZE ##################################
    # ==============================================================================
    paths.initialize_directories()
    daily_paths = paths.get_daily_paths(FORMATTED_DATE)
    logger = config_log.setup_logging(daily_paths["log"])
    config_log.print_log_separator("Starting Radiobinding Script")

    # ==============================================================================
    # ########################### VALIDATE CONFIG FILES ############################
    # ==============================================================================
    config_log.print_log_separator("Validating Config Files")
    try:
        user_config = validators.validate_user_config(paths.USER_CONFIG_PATH, paths.DATA_FILES_DIR)
        validators.validate_rad_archive_file(paths.RADIOACTIVITY_PATH, paths.RADIOACTIVITY_TEMPLATE_PATH)
    except (ValueError, KeyError, FileNotFoundError, RuntimeError) as e:
            # One catch-all for critical setup errors
            logger.critical(f"Startup failed: {e}", exc_info=True)
            sys.exit(1)


    # ==============================================================================
    # ############################ LOAD TEXT FILES #################################
    # ==============================================================================
    config_log.print_log_separator("Loading Text Files")
    inputs.create_blank_file(daily_paths["barcode"])
    inputs.create_blank_file(daily_paths["worklist"])
    try:
        inputs.open_or_print_file(daily_paths["barcode"], action="open")
        inputs.open_or_print_file(daily_paths["worklist"], action="open")
    except Exception as e:
        logger.critical(f"Failure Loading File: {e}")
        sys.exit(1)
    inputs.prompt_user_input()

    # ==============================================================================
    # ######################### VALIDATE TEXT FILES ################################
    # ==============================================================================
    config_log.print_log_separator("Validating Text Files")
    barcode_raw = inputs.load_text_files(daily_paths["barcode"])
    worklist_raw = inputs.load_text_files(daily_paths["worklist"])
    try:
        validators.validate_input(barcode_raw, worklist_raw)
    except (ValueError) as e:
        logger.critical(f"Text File Validation Failed: {e}")
        sys.exit(1)

    # ==============================================================================
    # ################ CREATE PANDAS DATAFRAME FOR INPUT FILES #####################
    # ==============================================================================
    config_log.print_log_separator("Merging Text Files")
    df = processing.merge_intial_inputs(
        barcode_raw=barcode_raw,
        worklist_raw=worklist_raw,
        receptor_mapping=processing.RECEPTOR_MAPPING
        )

    # ==============================================================================
    # #################### AUTHENTICATE GOOGLE CREDENTIALS #########################
    # ==============================================================================
    config_log.print_log_separator("Authenticating Google Sheets")
    creds = Credentials.from_service_account_file(user_config["gsheet_auth_path"], scopes=gsheet_auth.SCOPE)
    client = gspread.authorize(creds)
    logging.info('google credientals authenticated')

    # ==============================================================================
    # ######################## READ IN GOOGLE SHEET DATA ###########################
    # ==============================================================================
    # TODO: Let script run optionally offline with local assay csv's
    config_log.print_log_separator("Load Google Sheet Databases")
    gsheet_database_dfs = gsheet_auth.load_all_gsheet_db(
        client,
        gsheet_auth.GSHEET_FILE_NAME,
        gsheet_auth.GSHEET_CONFIG
        )

    # ==============================================================================
    # #################### VALIDATE GSHEET DATABASES COLUMNS #######################
    # ==============================================================================
    config_log.print_log_separator("Validating Google Sheet Database's Columns")
    try:
        validators.val_gsheet_dfs_cols(
            gsheet_database_dfs,
            gsheet_auth.GSHEET_CONFIG
        )
    except (KeyError, ValueError) as e:
        logger.critical(f"Google Sheet Database Validation Failed: {e}")
        sys.exit(1)

    # ==============================================================================
    # ######################### FORMAT GSHEET DATABASES ############################
    # ==============================================================================
    config_log.print_log_separator("Formatting Google Sheet Databases")
    try:
        gsheet_database_dfs = processing.format_gsheet_dfs(
                gsheet_database_dfs=gsheet_database_dfs,
                gsheet_config=gsheet_auth.GSHEET_CONFIG
            )
    except (Exception) as e:
        logger.critical(f"Formatting Google Sheet Databases failed: {e}")
        sys.exit(1)

    # ==============================================================================
    # ############### VALIDATE GSHEET DATABASES POST-FORMATTING ####################
    # ==============================================================================
    # TODO: Write a function that verifies the values in columns after formatting
    # TODO: Radionuclide = "I125/H3", Filtertype = "Filtermat/Unifilter"
    # TODO: Binding Type = "PRIM/SEC" (should have been confirmed), etc.

    # ==============================================================================
    # ################## MERGE INPUT DF AND GSHEET DATABASES #######################
    # ==============================================================================
    config_log.print_log_separator("Merging Input DF's and GSHEET DF's")
    try:
        df = processing.merge_dfs(
            input_df=df,
            gsheet_database_dfs=gsheet_database_dfs
        )
    except (KeyError) as e:
        logger.critical(f"Failed to Merge: {e}")
        sys.exit(1)


    # ==============================================================================
    # ############### CALCULATE HOT USAGE & PELLET USAGE PER ASSAY #################
    # ==============================================================================
    config_log.print_log_separator("calculating radioactive material & pellet usage")
    df = processing.calc_material_usage(
        now=NOW,
        df=df
        )

    # ==============================================================================
    # ###################### CREATE SUMMARY DATAFRAMES #############################
    # ==============================================================================
    config_log.print_log_separator("creating summary dataframes")
    summary_df, log_df = processing.aggregate_df(
        df = df,
        user_initals=user_config["user_initials"],
        user_name=user_config["user_name"]
        )

    # ==============================================================================
    # ################### WRITE TO LOCAL ARCHIVE EXCEL FILE ########################
    # ==============================================================================
    config_log.print_log_separator("writing to radioactive archive excel sheet")
    excel_writer.write_archive_excel(
        archive_sheet_path=paths.RADIOACTIVITY_PATH,
        df=df,
        column_schema=excel_writer.ARCHIVE_COLUMN_SCHEMA,
        user_config=user_config,
        gray_switch_name="gray_switch",
        user_config_path=paths.USER_CONFIG_PATH,
        starting_plate_index=excel_writer.STARTING_PLATE_INDEX
    )

    # ==============================================================================
    # ################## WRITE TO BINDING PRINTOUT EXCEL FILE ######################
    # ==============================================================================
    config_log.print_log_separator("Writing to binding printout")
    with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            logger.info(f"Created temporary directory: {tmp_dir}")
            temp_binding_printout_path = tmp_dir / daily_paths["printout_basename"]

            excel_writer.write_printout(
                printout_template_path=paths.PRINTOUT_TEMPLATE_PATH,
                printout_dest_path=temp_binding_printout_path,
                printout_column_schema=excel_writer.PRINTOUT_COLUMN_SCHEMA,
                summary_df=summary_df,
                now=NOW,
                starting_plate_index=excel_writer.STARTING_PLATE_INDEX
                )
            
            paths.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            
            desired_target = paths.ARCHIVE_DIR / daily_paths["printout_basename"]
            binding_printout_path = processing.get_unique_path(desired_target)
            
            shutil.move(str(temp_binding_printout_path), str(binding_printout_path))
            logger.info(f"Successfully archived to: {binding_printout_path}")


    # ==============================================================================
    # ################ WRITE TO GOOGLE SHEET HOT & PELLET LOGS #####################
    # ==============================================================================
    config_log.print_log_separator("Writing Log to Google Sheets")
    gsheet_auth.write_log_gsheet(
        client=client,
        gsheet_file_name=gsheet_auth.GSHEET_FILE_NAME,
        log_df=log_df,
        gsheet_config=gsheet_auth.GSHEET_CONFIG
    )

    # ==============================================================================
    # ############################# OPEN & PRINT FILES #############################
    # ==============================================================================
    config_log.print_log_separator("Printing and Opening files")
    inputs.open_or_print_file(filepath=paths.RADIOACTIVITY_PATH, action="open")
    inputs.open_or_print_file(filepath=binding_printout_path, action="print")

    # ==============================================================================
    # ######################### MOVE FILES TO ARCHIVE DIR ##########################
    # ==============================================================================
    config_log.print_log_separator("Moving input files to archive folder")
    processing.move_input_files(daily_paths=daily_paths, dest_dir=paths.ARCHIVE_DIR)

    config_log.print_log_separator("done :/)")


if __name__ == "__main__":
    main()

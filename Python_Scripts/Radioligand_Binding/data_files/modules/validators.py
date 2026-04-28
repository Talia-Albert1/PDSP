from .inputs import run_config_setup_wizard
import logging
from pathlib import Path
import json
import sys
import shutil
import pandas as pd
logger = logging.getLogger(__name__)

def validate_user_config(user_config_path:Path) -> dict[str, str]:
    """Validates user_config.json file exists
    Validates the following columns exist:
    ['user_name', 'user_initials', 'gray_switch']
    
    Returns dict

    Parameters
    ----------
    user_config_path : str
        Path to user_config.json file

    Returns
    -------
    dict[str, str]
        dict with ['user_name', 'user_initials', 'gray_switch']

    """
    while True:
        # If file doesn't exist, create it by prompting the user
        if not user_config_path.exists():
            run_config_setup_wizard(user_config_path)
        
        # necessary columns
        required_fields = ['user_name', 'user_initials', 'gray_switch']

        # Load the file
        try:
            with open(user_config_path, 'r') as f:
                user_config = json.load(f)

            missing = [field for field in required_fields if not user_config.get(field, None)]
            if missing:
                raise KeyError(f"Config is missing required fields: {missing}")

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Config error: {e}")
            logger.error(f"The config file at {user_config_path} is corrupted or invalid")
            prompt = input("\n Would you like to delete the file and create a new user_config.json (Y/N): ").strip().lower()

            if prompt == "y":
                user_config_path.unlink(missing_ok=True)
                logger.info("User opted to delete config file and restart setup")
                continue
            
            else:
                raise RuntimeError("User declined to repair the corrupted configuration file.")
        # Verify required fields are present and not empty
        
        logger.info(f"user_config.json loaded for: {user_config['user_name']} ({user_config['user_initials']})")
        return user_config




def validate_radioactivity_archive_file(
        radioactivity_path         : Path,
        radioactivity_template_path: Path
    ) -> None:
    """Verifies the Radioactivity Archive Exists, if it does not, the template is
    copied from Data_Files_Dir into the root.

    Parameters
    ----------
    radioactivity_path : str, optional
        The default is RADIOACTIVITY_PATH.
    radioactivity_template_path : str, optional
        The default is RADIOACTIVITY_TEMPLATE_PATH.

    Returns
    -------
    None
    """
    # copy template to root if it does not exist
    if not radioactivity_path.exists():
        if not radioactivity_template_path.exists():
            raise FileNotFoundError(f"Radioactivity Archive template missing from data files dir: {radioactivity_template_path}")
        shutil.copy2(radioactivity_template_path, radioactivity_path)

        if not radioactivity_path.exists:
            raise RuntimeError(f"Failed to create {radioactivity_path} after copy")
        logger.info(f"Radioactivity Archive Intialized: "
                    f"{radioactivity_template_path} copied to {radioactivity_path}"
                    )

    else:
        logger.info(f"{radioactivity_path} - exists")
        return





def validate_input(barcode_raw: list, worklist_raw: list) -> None:
    """
    Verifies that the files were populated and lists are not empty.
    Compiles errors into list, raises error back to main script via truthiness checks
    
    Raises:
        ValueError: If either list is None or empty.
    """
    # --------------------------------------------------------------------------------
    # ERRORS LIST
    # --------------------------------------------------------------------------------
    errors = []
    def compile_errors(list_of_errors:list) -> str:
        if errors:
            report = "\n- ".join(list_of_errors)
            raise ValueError(f"Validation failed with {len(list_of_errors)} error(s):\n- {report}")

    # --------------------------------------------------------------------------------
    # EMPTINESS CHECK
    # --------------------------------------------------------------------------------
    if not barcode_raw:
        errors.append("Barcode text file is empty or was not provided.")
    if not worklist_raw:
        errors.append("Worklist text file is empty or was not provided.")
    
    # --------------------------------------------------------------------------------
    # REPORT EMPTY ERRORS
    # --------------------------------------------------------------------------------
    if errors:
        compile_errors(errors)
    
    # --------------------------------------------------------------------------------
    # BARCODE VALIDATION
    # --------------------------------------------------------------------------------
    logger.info(f"Loaded {len(barcode_raw)} barcodes")

    # check for duplicate barcodes, should be none
    barcode_dupes = [b for b in barcode_raw if barcode_raw.count(b) > 1]
    if barcode_dupes:
        msg = f"Duplicate Barcodes: {', '.join(set(barcode_dupes))}"
        errors.append(msg)
    
    # --------------------------------------------------------------------------------
    # WORKLIST VALIDATION
    # --------------------------------------------------------------------------------
    logger.info(f"Loaded {len(worklist_raw)} worklist entries")

    # all lines should have 2 columns "Binding Type\tReceptorName-X"
    # column one should be "PRIM" or "SEC"
    erroneous_lines = []
    spelling_errors = []
    excpected_bt_values = ["PRIM", "SEC"]
    binding_type_list = []
    for i, line in enumerate(worklist_raw):
        columns = line.split('\t')
        
        # if not 2 columns, error
        if len(columns) != 2:
            erroneous_lines.append(f"Row {i}: {line}")    

        elif columns:
            binding_type = columns[0].upper().strip()

            if binding_type not in excpected_bt_values:
                spelling_errors.append(f"Row {i}: Incorrect Label:{columns[1]}")
            
            binding_type_list.append(binding_type)


    if erroneous_lines:
        msg = f"Worklist rows missing tab-delimiter: {'; '.join(erroneous_lines)}"
        logger.warning(msg)
        errors.append(msg)
    
    if spelling_errors:
        msg = f"Worklist rows without 'PRIM' or 'SEC' in first column: {'; '.join(spelling_errors)}"
        logger.warning(msg)
        errors.append(msg)
    
    # --------------------------------------------------------------------------------
    # BARCODE COUNTS
    # --------------------------------------------------------------------------------
    num_barcodes_barcode = len(barcode_raw)
    prim_count = sum(1 for bt in binding_type_list if bt == "PRIM")
    sec_count = sum(1 for bt in binding_type_list if bt == "SEC")
    num_barcodes_worklist = prim_count + (sec_count * 3)

    if num_barcodes_barcode != num_barcodes_worklist:
        msg_1 = (f"Number of Barcodes from Barcode text file: {num_barcodes_barcode}")
        msg_2 = (f"Number of Barcodes from Worklist text file: {num_barcodes_worklist}")    
        logger.warning(msg_1)
        logger.warning(msg_2)
        errors.append(msg_1)
        errors.append(msg_2)

    else:
        logger.info(f"Number of Barcodes from Barcode file and Worklist file match: {num_barcodes_barcode} barcodes")
        
    # --------------------------------------------------------------------------------
    # REPORT ERRORS IF THERE ARE ANY
    # --------------------------------------------------------------------------------
    if errors:
        compile_errors(errors)





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
    
    Raises:
        ValueError: If either list is None or empty.
    """
    # emptiness check
    if not barcode_raw:
        raise ValueError("Barcode text file is empty or was not provided.")
        
    if not worklist_raw:
        raise ValueError("Worklist text file is empty or was not provided.")
    
    # barcode validation
    logger.info(f"Loaded {len(barcode_raw)} barcodes")
    barcode_dupes = [b for b in barcode_raw if barcode_raw.count(b) > 1]
    if barcode_dupes:
        raise ValueError(f"Duplicate Barcodes: {', '.join(set(barcode_dupes))}")


    
    logger.info(f"Loaded {len(worklist_raw)} worklist entries")

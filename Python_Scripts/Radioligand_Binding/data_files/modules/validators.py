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
    user_config_path : str, optional
        Path to user_config.json file

    Returns
    -------
    dict[str, str]
        dict with ['user_name', 'user_initials', 'gray_switch']

    """
    # If file doesn't exist, create it by prompting the user
    if not user_config_path.exists():
        logger.info(f"No user_config.json at: {user_config_path}, "
                    "creating new one..."
                    )
        print('\nNo user config file found. Please enter your information:')
        
        while True:
            # Prompt user to input info for JSON
            user_name = input("Enter your first name: ").strip()
            user_initials = input("Enter your initials: ").strip()
            gray_switch = 1  # default starting value
            
            # Confirm with user
            print('\nPlease verify your information:')
            print(f'  Name:     {user_name}')
            print(f'  Initials: {user_initials}')
            confirm = input('Is this correct? (Y/N): ').strip().lower()
            
            if confirm == 'y':
                user_config = {
                    'user_name': user_name,
                    'user_initials': user_initials,
                    'gray_switch': gray_switch
                }
                with open(user_config_path, 'w') as f:
                    json.dump(user_config, f, indent=4)
                logger.info(f'user_config.json created at: {user_config_path}')
                break
            else:
                print('Let\'s try again...\n')
    
    # Load the file
    try:
        with open(user_config_path, 'r') as f:
            user_config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Config at {user_config_path} is not valid JSON: {e}")
    
    # Verify required fields are present and not empty
    required_fields = ['user_name', 'user_initials', 'gray_switch']
    missing = [field for field in required_fields if not user_config.get(field, None)]

    if missing:
        raise KeyError(f"Config is missing required fields: {missing}")
    
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
            raise FileNotFoundError(f"Required template missing: {template_path}")
        shutil.copy2(radioactivity_template_path, radioactivity_path)
        logger.info(f"{radioactivity_template_path} copied to {radioactivity_path}")
    else:
        logger.info(f"{radioactivity_path} - exists")

    return





def validate_input(barcode_raw: list, worklist_raw: list) -> None:
    """
    Verifies that the files were populated and lists are not empty.
    
    Raises:
        ValueError: If either list is None or empty.
    """
    if not barcode_raw:
        raise ValueError("Barcode list is empty or was not provided.")
        
    if not worklist_raw:
        raise ValueError("Worklist list is empty or was not provided.")

    logger.info(f"Loaded {len(barcode_raw)} barcodes")
    logger.info(f"Loaded {len(worklist_raw)} worklist entries")

import logging
from pathlib import Path
import json
import sys
import shutil
import pandas as pd
logger = logging.getLogger(__name__)

def verify_user_config(user_config_path:Path) -> dict[str, str]:
    """
    Verifies user_config.json file exists
    Verifies the following columns exist:
    ['user_name', 'user_initials', 'gray_switch']
    
    Returns dict

    Parameters
    ----------
    user_config_path : str, optional
        DESCRIPTION. The default is USER_CONFIG_PATH.

    Returns
    -------
    dict[str, str]
        DESCRIPTION.

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
        logging.error(f'user_config.json is malformed and could not be read: {e}')
        sys.exit(1)
    
    # Verify required fields are present and not empty
    required_fields = ['user_name', 'user_initials', 'gray_switch']
    missing = [field for field in required_fields if not user_config.get(field, None)]
    if missing:
        logger.error(f"user_config.json is missing or has empty fields: {missing}")
        sys.exit(1)
    
    logger.info(f"user_config.json loaded for: {user_config['user_name']} ({user_config['user_initials']})")
    return user_config




def verify_radioactivity_archive_file(
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
            logger.error(f"Missing {radioactivity_template_path}, ensure file is present")
            sys.exit(1)
        shutil.copy2(radioactivity_template_path, radioactivity_path)
        logger.info(f"{radioactivity_template_path} copied to {radioactivity_path}")
    else:
        logger.info(f"{radioactivity_path} - exists")

    return





def verify_input_df (barcode_df: pd.DataFrame, worklist_df: pd.DataFrame) -> None:
    """Verifies that the Worklist and Barcode text files were populated correctly, and ensures the
    number of barcodes matches what is expected.

    Args:
        barcode_df (pd.DataFrame, optional): _description_. Defaults to barcode_df.
        worklist_df (pd.DataFrame, optional): _description_. Defaults to worklist_df.

    Raises:
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """
    # Verify Barocde dataframe
    # Ensure there are no blanks
    if barcode_df is None or worklist_df is None:
        logger.error("User cancelled or closed input window")
        sys.exit(1)

    logger.info(f"Loaded {len(barcode_df)} barcodes")
    logger.info(f"Loaded {len(worklist_df)} worklist entries")
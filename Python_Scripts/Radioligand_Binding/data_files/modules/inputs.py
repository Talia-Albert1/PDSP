import logging
from pathlib import Path
import pandas as pd
import os
import platform
import subprocess
import json



logger = logging.getLogger(__name__)

def choose_file(data_files_dir: Path) -> str:
    """_summary_

    Args:
        data_files_dir (Path): _description_
        json (str, optional): _description_. Defaults to "json".

    Returns:
        Path: _description_
    """
    # generate list of candidate files, in there are none, raise an error
    auth_candidates = list(data_files_dir.glob('*.json'))

    if not auth_candidates:
        raise FileNotFoundError(f"No Google Sheets json file in {data_files_dir}")
    
    # create a list of valid choices, used for choice validation later
    valid_choices = list(range(len(auth_candidates) + 1))

    # choice selection
    while True:
        print(f"\nPlease choose the Google Sheets .json")
        print(f"0: Not using Google Sheets, using the script offline")
        for i, file in enumerate(auth_candidates):
            print(f"{i + 1}: {file.name}")

        user_input = input(f"Please choose the Google Sheets .json:")

        if not user_input.isdigit():
            print("Please enter a number.")
            continue

        user_input = int(user_input)

        # if invalid choice, print menu again
        if user_input not in valid_choices:
            print(f"{user_input} not a valid choice, please pick again")
            continue
        
        # if valid choice, return 0 or 
        else:
            if user_input == 0:
                gsheet_auth_path = ""
            else:
                # index is offset by 0 to allow for not using the file as an option
                file_index = user_input - 1
                # str gives full path, want to return str object for json
                gsheet_auth_path = str(data_files_dir / Path(auth_candidates[file_index]))

            logger.info(f"gsheet_auth_path chosen to be: {gsheet_auth_path}")
            return gsheet_auth_path




def run_config_setup_wizard(user_config_path: Path, data_files_dir: Path) -> None:
    print('\n--- User Configuration Setup ---')
    
    while True:
        user_name = input("Enter your first name: ").strip()
        user_initials = input("Enter your initials: ").strip()
        gray_switch = 1
        
        if not user_name or not user_initials:
            print("Fields cannot be empty. Please try again.")
            continue

        print('\nPlease verify your information:')
        print(f'  Name:     {user_name}')
        print(f'  Initials: {user_initials}')
        confirm = input('Is this correct? (Y/N): ').strip().lower()
        if confirm == 'y':
            user_config = {
                'user_name'       : user_name,
                'user_initials'   : user_initials,
                'gray_switch'     : gray_switch
            }
            logger.info("Name and initals confirmed")
        else:
            print('Let\'s try again...\n')
            continue
        
        gsheet_auth_path = choose_file(data_files_dir)
        user_config.update({'gsheet_auth_path': gsheet_auth_path})
        with open(user_config_path, 'w') as f:
            json.dump(user_config, f, indent=4)
            
        logger.info(f"New config created at {user_config_path}")
        break


# Create Barcodes.txt or worklist.txt
def create_blank_file(file_path: Path)->None:
    """Creates files at path if they do not exist.
    Used Barcode and Worklist text file creation."""
    if os.path.exists(file_path):
        logger.info(f"{file_path} text file already exists")
    else:
        with open(file_path, 'w') as file:
            file.write('')
    return



# Generalized function to open or print files
def open_or_print_file(filepath: Path, action: str="open")->None:
    """Open or Print a file, operating system agnostic
    Parameters
    ----------
    filepath : str
        path of file to open
    action : str, optional
        default to "open", other option is "print"
    
    Returns
    -------
    None
    """
    try:
        if platform.system() == 'Windows':
            if action == "print":
                os.startfile(filepath, 'print')
            else:
                os.startfile(filepath)
        elif platform.system() == 'Darwin':  # macOS
            if action == "print":
                subprocess.call(('lpr', filepath))
            else:
                subprocess.call(('open', filepath))
        else:  # Linux and other Unix-like systems
            if action == "print":
                subprocess.call(('lp', filepath))
            else:
                subprocess.call(('xdg-open', filepath))
    except Exception as e:
        raise Exception(f"Failed to {action} {filepath}: {e}")




def prompt_user_input()-> None:
    """Prompts user to proceed script after completing text files"""
    while True:
        user_input = input("Enter 'y' when ready to proceed: ").strip().lower()
        
        if user_input == 'y':
            print("Great! Proceeding...")
            break
        else:
            print("Invalid input. Please enter 'Y' to proceed.")







def load_text_files(file_path: Path) -> list[str]:
    """Reads in text file and returns list of strings"""
    with open(file_path, 'r') as f:
        # get non-empty lines
        lines = [line.strip() for line in f if line.strip()]

    return lines



import logging
from pathlib import Path
import pandas as pd
import os
import platform
import subprocess
import json



logger = logging.getLogger(__name__)

def run_config_setup_wizard(user_config_path: Path) -> None:
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
                'user_name': user_name,
                'user_initials': user_initials,
                'gray_switch': gray_switch
            }
            
            with open(user_config_path, 'w') as f:
                json.dump(user_config, f, indent=4)
            
            logger.info(f"New config created at {user_config_path}")
            break
        else:
            print('Let\'s try again...\n')


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







def load_text_files(file_path: Path) -> list:
    """Reads in text file and returns list of lines"""
    with open(file_path, 'r') as f:
        # get non-empty lines
        lines = [line.strip() for line in f if line.strip()]

    return lines



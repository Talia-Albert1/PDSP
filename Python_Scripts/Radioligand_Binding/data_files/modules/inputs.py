import logging
from pathlib import Path
import pandas as pd
import os
import platform
import subprocess



logger = logging.getLogger(__name__)

# Create Barcodes.txt or worklist.txt
def create_blank_file(file_path: Path)->None:
    """Creates files at path if they do not exist.
    For Barcode and Worklist text file creation."""
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
        print(f"Failed to {action} {filepath}: {e}")




def prompt_user_input()-> None:
    while True:
        user_input = input("Enter 'y' when ready to proceed: ").strip().lower()
        
        if user_input == 'y':
            print("Great! Proceeding...")
            break
        else:
            print("Invalid input. Please enter 'Y' to proceed.")







def load_text_files(file_path: Path, file_type: str) -> pd.DataFrame:
    """Loads a text file into a DataFrame.

    Args:
        file_path (str): Path to the text file.
        file_type (str): Type of file, either 'barcode' or 'worklist'.

    Returns:
        pd.DataFrame: Loaded data.

    Raises:
        ValueError: If file_type is not 'barcode' or 'worklist'.
    """
    with open(file_path, 'r') as f:
        if file_type == "barcode":
            barcodes = [line.strip() for line in f]
            df = pd.DataFrame(barcodes, columns=["Barcode"])

        elif file_type == "worklist":
            binding_types = []
            plate_names = []
            for line in f:
                columns = line.strip().split('\t')
                binding_types.append(columns[0])
                plate_names.append(columns[1])
            df = pd.DataFrame({
                'Binding Type': binding_types,
                'Plate Name': plate_names
            })

        else:
            raise ValueError(f"Unknown file_type '{file_type}'. Expected 'barcode' or 'worklist'.")
    
    logger.info(f"{file_type} text file loaded from {file_path}, shape of dataframe {df.shape}")

    return df
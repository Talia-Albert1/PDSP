# -*- coding: utf-8 -*-
# utils.py
import os
import sys
import logging
import shutil
import csv
import platform
import subprocess

# Write log messages
def setup_logging(log_dir, log_filename='log.log'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        filename=log_file_path,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Also add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)


# Create directories used by *most* scripts
def setup_dir(create_output_dir='y', create_data_files_dir='y'): 
    current_dir = os.getcwd()
    archive_dir = os.path.join(current_dir, "archive")
    input_dir = os.path.join(current_dir, "input")

    # Ensure the necessary directories exist
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)

    # Conditionally create the data_files_dir
    data_files_dir = None
    if create_data_files_dir == 'y':
        data_files_dir = os.path.join(current_dir, "data_files")
        os.makedirs(data_files_dir, exist_ok=True)

    # Conditionally create the output_dir
    output_dir = None
    if create_output_dir == 'y':
        output_dir = os.path.join(current_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

    # Return paths based on what was created
    if create_output_dir == 'y' and create_data_files_dir == 'y':
        return current_dir, archive_dir, data_files_dir, input_dir, output_dir
    elif create_output_dir == 'y':
        return current_dir, archive_dir, input_dir, output_dir
    elif create_data_files_dir == 'y':
        return current_dir, archive_dir, data_files_dir, input_dir
    else:
        return current_dir, archive_dir, input_dir

# Select a file from input
def select_file_from_input_dir(input_dir, return_filename=False):
    # Get a list of files in the input directory
    try:
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    except FileNotFoundError:
        logging.info(f"Directory '{input_dir}' does not exist.")
        sys.exit(1)

    # If there are no files, inform the user and exit
    if not files:
        logging.info("No files found in the input directory.")
        sys.exit(1)
    
    # If there is only one file, use that file
    if len(files) == 1:
        logging.info(f"Only one file found: {files[0]}")
        selected_file = files[0]
    else:
        # If there are multiple files, display them and prompt the user to select one
        logging.info("Select a file from the list:")
        for i, file_name in enumerate(files):
            logging.info(f"{i + 1}: {file_name}")
        
        # Get the user's selection
        while True:
            try:
                choice = int(input(f"Enter a number (1-{len(files)}): "))
                if 1 <= choice <= len(files):
                    selected_file = files[choice - 1]
                    break
                else:
                    logging.warning(f"Invalid choice. Please select a number between 1 and {len(files)}.")
            except ValueError:
                logging.warning("Invalid input. Please enter a number.")
    
    # Construct the full path
    full_path = os.path.join(input_dir, selected_file)
    
    # Return both values, depending on `return_filename`
    if return_filename:
        return full_path, selected_file  # Returns full path and file name separately
    else:
        return full_path  # Only returns the full path



# Generalized function to open or print files
def open_or_print_file(filepath, action="open"):
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

# To open a file
def open_file(filepath):
    open_or_print_file(filepath, action="open")

# To print a file
def print_file(filepath):
    open_or_print_file(filepath, action="print")

# Copy's files initally
def copy_and_rename(source_path, destination_path):
    if not os.path.exists(destination_path):
        shutil.copy(source_path, destination_path)
        logging.info(f"File created at {destination_path}")

def move_dir_files(source_dir, destination_dir):
    # Check if source_dir exists
    if not os.path.exists(source_dir):
        logging.info(f"Directory '{source_dir}' does not exist.")
        return

    # Get a list of all files in source_dir
    files = os.listdir(source_dir)

    # If there are no files in source_dir
    if not files:
        logging.info(f"No files found in '{source_dir}' to move.")
        return

    # Ensure destination_dir exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Loop through the files and move each one to destination_dir
    for file_name in files:
        file_path = os.path.join(source_dir, file_name)
        
        if os.path.isfile(file_path):  # Only move files, not directories
            dest_path = os.path.join(destination_dir, file_name)

            # If file with same name exists in destination, add suffix
            if os.path.exists(dest_path):
                base_name, extension = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(dest_path):
                    # Add (counter) suffix before the extension
                    new_name = f"{base_name}({counter}){extension}"
                    dest_path = os.path.join(destination_dir, new_name)
                    counter += 1

            # Move the file to the new destination with the appropriate name
            shutil.move(file_path, dest_path)
            logging.info(f"Moved: {file_name} to {dest_path}")

def move_and_rename_file(source_path, destination_dir, new_name):
    # Check if the source file exists
    if not os.path.exists(source_path):
        logging.info(f"File '{source_path}' does not exist.")
        return

    # Ensure the destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Construct the new file path with the new name
    new_file_path = os.path.join(destination_dir, new_name)

    # Move and rename the file
    shutil.move(source_path, new_file_path)
    logging.info(f"Moved and renamed file to: {new_file_path}")

# Move archive and disposal files
def intial_files(data_files_dir, current_dir, inital_name, final_name):
    source_dir = os.path.join(data_files_dir, inital_name)
    destination_dir = os.path.join(current_dir, final_name)
    copy_and_rename(source_dir, destination_dir)

# Gray switch file creation
def create_gray_switch(data_files_dir):
    gray_switch_dir = os.path.join(data_files_dir, 'Gray_Switch.txt')
    if not os.path.isfile(gray_switch_dir):
        with open(gray_switch_dir, 'w') as text_file:
            text_file.write('1')
            logging.info(f"Gray_Switch.txt created at {data_files_dir}")
    return gray_switch_dir

# Create Barcodes.txt or worklist.txt
def create_inital_txtfile(input_dir, txt_name):
    text_file_dir = os.path.join(input_dir, txt_name + '.txt')
    if os.path.exists(text_file_dir):
        logging.info(f'{txt_name} text file already exists')
    else:
        with open(text_file_dir, 'w') as file:
            file.write('')
        open_file(text_file_dir)
    return text_file_dir

# Proceed when user enters Y
def wait_for_confirmation():
    while True:
        user_input = input("Enter Y when ready to proceed: ").strip().lower()

        if user_input == 'y':
            logging.info("Great! Proceeding...")
            break
        else:
            logging.warning("Invalid input. Please enter 'Y' to proceed.")

def load_data_from_file(file_path, delimiter=None, log_message=None):
    # Initialize an empty list to store the table data
    data = []

    # Read the file
    with open(file_path, 'r') as text_file:
        for line in text_file:
            # Split the line into columns based on the provided delimiter
            if delimiter:
                columns = line.strip().split(delimiter)
            else:
                columns = line.strip()

            # Append the columns to the data list
            data.append(columns)

            # Log the columns
            logging.info(columns)

    # Log a custom message if provided
    if log_message:
        logging.info(log_message)

    return data

def read_csv_file(file_path, remove_header=False):
    # Check if the file exists
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return []

    # Initialize a list to store rows
    data = []

    # Open the file and read the content
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            
            # Read the header row (optional)
            if remove_header:
                next(csvreader)

            # Read each row and add it to the data list
            for row in csvreader:
                data.append(row)
            
            logging.info('CSV file read successfully')
            
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return []

    return data

def unique_column_in_list(data, column_index):
    # Check if the data is empty
    if not data:
        raise ValueError("The input data cannot be empty.")

    # Check if the column index is valid
    if column_index < 0 or column_index >= len(data[0]):
        raise ValueError("Invalid column index.")

    # Initialize a set to store unique entries
    unique_entries = set()

    # Loop through each row and add the specified column entry to the set
    for row in data:
        unique_entries.add(row[column_index])

    # Convert the set to a list and return it
    return list(unique_entries)

def write_list_to_csv(file_path, data_list):
    # Open the file in write mode
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the list as a row
        for item in data_list:
            writer.writerow([item])

def write_lists_to_file(file_path, list_of_lists):
    with open(file_path, 'a') as file:
        for sublist in list_of_lists:
            line = '\t'.join(map(str, sublist))  # Convert each element to a string and join with tabs
            file.write(line + '\n')  # Write the line to the file with a newline at the end


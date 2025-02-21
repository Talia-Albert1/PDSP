# -*- coding: utf-8 -*-
import shutil
import datetime
import os
import logging
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)
import utils


# Get directories & create those which do not exist
current_dir, archive_dir, input_dir, output_dir = utils.setup_dir(create_data_files_dir='n')

# Format the date as 'YYYYMMDD'
formatted_date = datetime.date.today().strftime('%Y%m%d')

# Setup logging functionality
utils.setup_logging(archive_dir,log_filename=formatted_date + '_log.log')

# Get the scanner's csv file directory
scannercsv_file_dir, scannercsv_file_name = utils.select_file_from_input_dir(input_dir,return_filename=True)

# Import the CSV into python (without header)
# Structure is DateScanned,Time,Column,Row,CompoundNumber
scannercsv = utils.read_csv_file(scannercsv_file_dir)

# Remove 'No Tube' lists
filtered_scannercsv = [lst for lst in scannercsv if lst[4] != "No Tube"]

# Remove DateScanned & Time, Swap Column & Row placement
scannercsv_formatted = []
for compound in filtered_scannercsv:
    scannercsv_formatted.append([compound[3], int(compound[2]), compound[4]])

# Header row of text file
header_row = [['Row', 'Column','Barcode']]

# Modify file name
final_scannercsv_file_name = scannercsv_file_name.replace('.csv','').replace('Scan', 'Text').replace('scan', 'Text')

# move files from output to archive
utils.move_dir_files(output_dir, archive_dir)

# Write to the text file
text_file_path = os.path.join(output_dir, final_scannercsv_file_name + '.txt')
utils.write_lists_to_file(text_file_path, header_row)
utils.write_lists_to_file(text_file_path, scannercsv_formatted)

# move files from input to archive
utils.move_dir_files(input_dir, archive_dir)

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 14:43:49 2023

@author: TaliaAlbert
"""
import os
import sys
import datetime
import logging
import shutil
import pandas as pd

import openpyxl
from openpyxl.styles import Border, Side, PatternFill, Font, Alignment
from openpyxl.formatting.rule import FormulaRule
import csv

import math
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, parent_dir)
import utils


# Get directories
current_dir, archive_dir, data_files_dir, input_dir, output_dir = utils.setup_dir(create_output_dir = 'y')

# Format the date as 'YYYY-MM-DD'
formatted_date = datetime.date.today().strftime('%Y%m%d')

# Setup logging functionality
log_file_name = f'{formatted_date}_Plate_Visualization_Tool_log.log'
utils.setup_logging(archive_dir, log_filename=log_file_name)


# Select Verso Plate Map
verso_num_files = int(input("Enter the number of Verso Plate Map files: "))
verso_plate_map_df = []
for i in range(verso_num_files):
    verso_message = f"Select the {i + 1} Plate Map file from the Verso (should end in \".txt\")"
    verso_plate_map_dir = utils.select_file_from_input_dir(input_dir, message = verso_message)
    verso_plate_map_file_name = os.path.basename(verso_plate_map_dir)
    try:
        # Read the file as a DataFrame and add a 'Source' column
        df = pd.read_csv(verso_plate_map_dir, sep='\t')
        df['Source_File'] = f'{verso_plate_map_file_name}'
        verso_plate_map_df.append(df)
    except Exception as e:
        print(f"Error reading file {i + 1}: {e}")


# Convert Barcode as Float64 to strings without a ".0"
for i in  range(verso_num_files):
    verso_plate_map_df[i]['Barcode'] = verso_plate_map_df[i]['Barcode'].fillna(-1).astype('Int64').astype(str)  # Convert int to string
    verso_plate_map_df[i] = verso_plate_map_df[i][verso_plate_map_df[i]['Barcode'] != '-1']




# Select Worklist file
worklist_num_files = int(input("Enter the number of Worklist files: "))
worklist_df = []
for i in range(worklist_num_files):
    worklist_message = "Select the worklist associated with this plate map file (should end in \".csv\")"
    worklist_file = utils.select_file_from_input_dir(input_dir, message = worklist_message)
    try:
        # Read the file as a DataFrame
        df = pd.read_csv(worklist_file, sep=',')
        worklist_df.append(df)
    except Exception as e:
        print(f"Error reading file {i + 1}: {e}")

# Convert Barcode "CMPD" to string
for i in  range(verso_num_files):
    worklist_df[i]['CMPD'] = worklist_df[i]['CMPD'].astype(str)  # Convert int to string
    worklist_df[i] = worklist_df[i][worklist_df[i]['CMPD'] != '-1']

unique_receptors = worklist_df[0]['Rec'].unique()





# Create Reference map for blank plates
plate_rows = ['A','B','C','D','E','F','G','H']
plate_columns = ['1','2','3','4','5','6','7','8','9','10','11','12']
row_column_list = []
well_number = 0
for row in plate_rows:
    for column in plate_columns:
        well_number += 1
        well_id = str(row) + str(column)
        row_column_list.append([well_id, well_number])


# https://stackoverflow.com/questions/15370432/writing-multi-line-strings-into-cells-using-openpyxl

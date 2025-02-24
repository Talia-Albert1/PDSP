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
verso_message = "Select the Plate Map file from the Verso (should end in \".txt\")"
verso_plate_map = utils.select_file_from_input_dir(input_dir, message = verso_message)

# Select Worklist file
worklist_message = "Select the worklist associated with this plate map file (should end in \".csv\")"
worklist_file = utils.select_file_from_input_dir(input_dir, message = worklist_message)

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:33:29 2023

@author: kealbert
"""

import os
import subprocess
import shutil
import time

# Get current directory
currentdir = os.getcwd() + '\\'
inputdir = currentdir + 'input\\'
outputdir = currentdir + 'output\\'
data_filesdir = currentdir + 'data_files\\'
archivedir = currentdir + 'archive\\'

# Get text file path
file_name = input('Enter Plate name:')
text_file_path = inputdir + file_name + '.txt'
if os.path.exists(text_file_path):
    print('Worklist text file already exists')
else:
    with open(text_file_path, 'w') as worklist_file:
        worklist_file.write('')
    
    try:
        # Open the text file with Notepad
        subprocess.Popen(['notepad.exe', text_file_path])
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Proceed input 
while True:
    user_input = input("Enter Y when ready to proceed: ").strip().lower()
    
    if user_input == 'y':
        print("Great! Proceeding...")
        break
    else:
        print("Invalid input. Please enter 'Y' to proceed.")

# Read text file
with open(text_file_path, 'r') as text_file:
    # Initialize an empty list to store the table data
    compounds = []
    
    # Read each line from the file
    for line in text_file:
        columns = line.strip()
        compounds.append(columns)

# Move contents of output to archive
output_files = os.listdir(outputdir)
for file in output_files:
    shutil.move(outputdir + file, archivedir)

# Generate singular list, save it as a text file and print it
output_for_worklist = ', '.join(compounds)
output_file_path = outputdir + file_name + '_worklist.txt'
with open(output_file_path, 'w') as file:
    file.write(output_for_worklist)
print(output_for_worklist)

shutil.move(text_file_path, archivedir)
time.sleep(20)



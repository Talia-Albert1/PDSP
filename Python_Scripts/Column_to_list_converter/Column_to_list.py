# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:33:29 2023

@author: kealbert
"""

import os
import shutil
import time

# Get current directory
currentdir = os.getcwd() + '\\'
inputdir = currentdir + 'input\\'
outputdir = currentdir + 'output\\'
data_filesdir = currentdir + 'data_files\\'
archivedir = currentdir + 'archive\\'

# Create directories if they do not exist
def create_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

create_directory(inputdir)
create_directory(archivedir)
create_directory(outputdir)

# Get text file path
file_name = input('Enter Plate name:')
text_file_path = inputdir + file_name + '.txt'
if os.path.exists(text_file_path):
    print('Text file already exists')
else:
    with open(text_file_path, 'w') as worklist_file:
        worklist_file.write('')
    
    try:
        # Open the text file with Notepad
        os.startfile(text_file_path)
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



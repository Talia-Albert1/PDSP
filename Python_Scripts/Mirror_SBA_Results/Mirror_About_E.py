# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 08:13:37 2024

@author: kealbert
"""
import os
import shutil

currentdir = os.getcwd() + '\\'
inputdir = currentdir + 'input\\'
outputdir = currentdir + 'output\\'
archivedir = currentdir + 'archive\\'

# Create Directories if they do not exist
def create_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

create_directory(inputdir)
create_directory(outputdir)
create_directory(archivedir)


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


with open(text_file_path, 'r') as file:
    lines = file.readlines()


# Extract the header (first row)
header = lines[0].strip()

# Extract the data rows
data_rows = lines[1:]

# Define the original row names
row_names = ["A", "B", "C", "D", "E", "F", "G", "H"]

# Swap rows A & H, B & G, C & F, D & E
# Note that data_rows[0] is 'A', data_rows[7] is 'H', etc.
mirrored_data = [
    data_rows[7].strip().split('\t', 1)[1],  # H
    data_rows[6].strip().split('\t', 1)[1],  # G
    data_rows[5].strip().split('\t', 1)[1],  # F
    data_rows[4].strip().split('\t', 1)[1],  # E
    data_rows[3].strip().split('\t', 1)[1],  # D
    data_rows[2].strip().split('\t', 1)[1],  # C
    data_rows[1].strip().split('\t', 1)[1],  # B
    data_rows[0].strip().split('\t', 1)[1],  # A
]

# Create the final mirrored rows with original row names
mirrored_rows = [f"{row_names[i]}\t{mirrored_data[i]}" for i in range(len(row_names))]

# Combine the header and the mirrored rows
output_lines = ["\t" + header] + mirrored_rows

# Move old data from output into archive
output_files = os.listdir(outputdir)
for file in output_files:
    shutil.move(outputdir + file, archivedir)

# Save output
mirrored_file_path = outputdir + file_name + '_mirrored.txt'
with open(mirrored_file_path, 'w') as file:
    file.write('\n'.join(output_lines) + '\n')

shutil.move(text_file_path, archivedir)
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:45:59 2023

@author: TaliaAlbert
"""

import os
import csv
import shutil

# Load Directories
currentdir = os.getcwd() + '\\'
inputdir = currentdir + 'input\\'
outputdir = currentdir + 'output\\'
data_filesdir = currentdir + 'data_files\\'
archivedir = currentdir + 'archive\\'

# Ensure each directory exists
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

if not os.path.exists(archivedir):
    os.makedirs(archivedir)





# Get verso export file path
inputdir_files = os.listdir(inputdir)
verso_export_file_path = inputdir + inputdir_files[0]

# Get star barcode template path
star_template_path = data_filesdir + 'Replace.txt'



# Open verso export csv
with open(verso_export_file_path, 'r') as csvfile:
    verso_barcodes = []
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        verso_barcodes.append(row)

# Remove the first entry as it is for the tube rack itself, which we are not interested in
verso_barcodes = verso_barcodes[1:]

# Isolate compound barcode from 'Identifier' Tag
for tube in verso_barcodes:
    barcode = tube['Identifier'].replace('[ECC 200] ', '')
    tube.update({'Barcode':barcode})
    print(barcode)

# Remove leading 0's
for tube in verso_barcodes:
    barcode = tube['Barcode'].lstrip('0') if tube['Barcode'].startswith('0') else tube['Barcode']
    tube.update({'Barcode':barcode})
    print(barcode)

# Determine the row and column from 'Location'
for tube in verso_barcodes:
    row = tube['Location'][0]
    column = tube['Location'][1:]
    tube.update({'Row':row, 'Column':column})
    print(column + ' ' + row)

# Create list of lines
with open(star_template_path, 'r') as text_file:
    # Initialize an empty list to store the table data
    star_template_list = []
    
    # Read each line from the file
    for line in text_file:
        # Split the line into columns based on tabs
        columns = line.strip().split('\t')
        
        # Append the columns to the table_data list
        star_template_list.append(columns)

# Remove first entry, I could remove it on the text file itself but I think for readability I will keep it
star_template_list = star_template_list[1:]

# Create dictionary for the star template
star_template = []
for entry in star_template_list:
    row = entry[0]
    column = entry[1]
    barcode = entry[2]
    star_template.append({'Row':row, 'Column':column, 'Barcode':barcode})

# Match positions and update barcodes
for barcode in verso_barcodes:
    for position in star_template:
        if barcode['Row'] == position['Row'] and barcode['Column'] == position['Column']:
            position.update({'Barcode':barcode['Barcode']})

# Remove 'replace' for remaining, unmatched positions
for position in star_template:
    if position['Barcode'] == 'replace':
        position.update({'Barcode':''})

# Move contents of output to archive
output_files = os.listdir(outputdir)
for file in output_files:
    shutil.move(outputdir + file, archivedir)

# Write template to text file
text_file_name = input('Please enter the name of the template:')
text_file_path = outputdir + text_file_name + '.txt'

with open(text_file_path, 'a') as file:
    file.write('Row\t')
    file.write('Column\t')
    file.write('Barcode\n')
    for position in star_template:
        file.write(position['Row'] + '\t')
        file.write(position['Column'] + '\t')
        file.write(position['Barcode'] + '\n')

# Move input into archive
shutil.move(verso_export_file_path, archivedir)

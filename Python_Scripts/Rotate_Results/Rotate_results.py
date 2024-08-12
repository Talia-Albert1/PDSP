import numpy as np
import os
import shutil

# Directory paths
currentdir = os.getcwd() + '/'
inputdir = currentdir + 'input/'
outputdir = currentdir + 'output/'
archivedir = currentdir + 'archive/'

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
file_name = input('Enter Plate name: ')
text_file_path = inputdir + file_name + '.txt'

# Check if the file exists
if not os.path.exists(text_file_path):
    print(f"File {text_file_path} does not exist. Exiting.")
    exit()

# Read the data from the file
with open(text_file_path, 'r') as file:
    lines = file.readlines()

# Process the header (first row of numbers)
header = lines[0].strip().split()

# Extract the data rows, ignoring the row labels (first column)
data = []
row_labels = []
for line in lines[1:]:
    split_line = line.strip().split()
    row_labels.append(split_line[0])  # Store the row label
    data.append([int(x) for x in split_line[1:]])  # Store the row data as integers

# Convert the data to a NumPy array for easier manipulation
data_array = np.array(data)

# Mirror the data both horizontally and vertically
mirrored_data_array = np.flipud(np.fliplr(data_array))

# Prepare the mirrored data for output
mirrored_rows = []
for i, row in enumerate(mirrored_data_array):
    mirrored_rows.append(f"{row_labels[i]}\t" + "\t".join(map(str, row)) + "\t")


# Combine the header and the mirrored rows
output_lines = ["\t" + "\t".join(header)] + mirrored_rows

# Move old data from output into archive
output_files = os.listdir(outputdir)
for file in output_files:
    shutil.move(outputdir + file, archivedir)

# Save output
mirrored_file_path = outputdir + file_name + '_rotated.txt'
with open(mirrored_file_path, 'w') as file:
    file.write('\n'.join(output_lines) + '\n')

print(f"Mirrored data saved to {mirrored_file_path}")

# Archive the input file
shutil.move(text_file_path, archivedir)
print(f"Original file moved to {archivedir}")

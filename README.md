# PDSP
 Information relevant to PDSP work

 The procedures folder contains the Tex and Markdown files, as well as compiled PDF's, of the procedures.

 The Python Scripts folder houses various python scripts used in the lab. The primary script we use is within the Daily_Radioactivity folder, Binding_Worksheet.py.

## Clone github repository
Clone the repository (download the files) by using the github desktop application, available here: https://desktop.github.com/


## How to use Daily_Radioactivity
### Downloads
Download the latest version of Python from here: https://www.python.org/downloads/

Once installed, use pip to download openpyxl, the package that we use to edit the Excel files we work with. Here: https://www.geeksforgeeks.org/how-to-install-openpyxl-in-python-on-windows/ has a great guide on how to do so.

1. Press the Windows key
2. Search for "cmd" and select the app "Command Prompt"
3. Copy and enter the following into the Command Prompt
```
py -m pip install openpyxl
```
It should be installed and working now!

### Configure some files
- Navigate to Daily_Radioactivity.
- Copy and Paste the blank templates for Radioactive_Disposal_log_blank.xlsx and Radioactivity_Archive_blank.xlsx so they are just within the Daily_Radioactivity folder.
- Remove the "_blank" from the end of each name

### Daily Use
Double click "Binding_Worksheet.py", and a terminal should appear, followed by 2 text files, YYYYMMDD_Worklist.txt and YYYYMMDD_Barcodes.txt.

In YYYYMMDD_Worklist.txt, copy and paste the plates from the worklist that are assigned for today. Copy both the cells indicating PRIM or SEC, and the cells with Receptor-X (where X is the plate number). Save the text file.

In YYYYMMDD_Barcodes.txt, enter the barcodes, from the plates, in the descending order that they appear in YYYYMMDD_Worklist.txt. Save the text file.

When both steps have been completed, navigate back to the terminal and enter "y" to proceed.

The script will then:
- Generate a printout for today's binding, including the ligands, ligand volumes, pellets, and buffers necessary
- The Radioactivity Archive sheet will open, with today's plates entered at the bottom of the sheet
- Radioactive_Disposal_log will be updated with the summary information about the uCi used and which ligands were consumed

### Trouble Shooting
**Ensure the Radioactive_Archive.xlsx sheet is saved and closed before entering "y" to proceed, the script will crash otherwise**

Ensure there are no duplicate files in both input and archive, and output and archive. Check the log file in the archive with today's date to get some diagnostic help, such as determining if the number of plates and number of barcodes are not equal.

If the script ran, but a mistake was made, the following can be done to undo the changes:
1. Cut and Paste today's Worklist and Barcode files from archive > input
2. Delete the printout in output
3. Open Radioactivity_Archive.xlsx and delete the rows from the most recent run (don't forget to save and close)
4. Open Gray_Switch.txt and change the number back to 0 or 1. If the last rows of Radioactivity_Archive are gray, change to 1, if they are white, change to 0.

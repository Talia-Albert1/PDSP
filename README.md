# PDSP

 Information relevant to PDSP work

 The procedures folder contains the Tex and Markdown files, as well as compiled PDF's, of the procedures.

 The Python Scripts folder houses various python scripts used in the lab. The primary script we use is the "Binding_Worksheet.py" script in the "Radioligand_Binding" directory

## Downloads

## Programs

- Download the latest version of Python from here: https://www.python.org/downloads/
- Download the GitHub desktop application, available here: https://desktop.github.com/
- Clone the repository (download the files) using the GitHub desktop application
- Install packages by double-clicking the "install_packages.py" file

### (Optional if install script fails) Install packages via terminal

If the install script failed to install packages for whatever reason, do the following to get the necessary packages installed.

1. Press the Windows key
2. Search for "cmd" and select the app "Command Prompt"
3. Navigate to the directory "/PDSP/Python_Scripts/Radioligand_Binding/"
4. Copy and enter the following into the Command Prompt

```bash

py -m pip install -r requirements.txt

```

## Google Cloud Project Setup

## Creating a Google Cloud Project

I have created a google cloud project using the PDSP google account. This URL: https://developers.google.com/workspace/guides/create-project is helpful for information around Google Cloud projects.

To access the project go to: https://console.cloud.google.com/
(PDSP-Google-Sheet-Writer)

## Add new users

We create a unique service account and JSON token for each member of the lab, which is necessary for python to read/write to our google sheet.

To view/add users open the project "Menu" > "IAM & Admin" > "Service Accounts" > "Create service account"

Create a name for the user, for example "Name-pdsp-writer"

### Create JSON tokens

Click the newly created accounts navigate to the "Keys" tab, "Add key" > "Create New Key" > "JSON"
Download the JSON and put it in the "data_files" directory of the Radioligand_Binding script.

"/PDSP/Python_Scripts/Radioligand_Binding/data_files/token_name.json"

### Share automated email with Google Sheet

Copy the email of the service account, and share it with the Google Sheet.

## How to Use

- Double click "Binding_Worksheet.py", a terminal window should open
- If it's the scripts first time running, you will be prompted to input your name, initals, and select a GSHEET json token
- 2 text files, "YYYYMMDD_Worklist.txt" and "YYYYMMDD_Barcodes.txt" will open
  - For "YYYYMMDD_Worklist.txt":
    - Populate the file with the binding type, tab, and then the plate name. Copying and pasting from Google Sheets will format it this way:
      - "PRIM(**tab**)receptor-XX"
      - "SEC(**tab**)receptor-XX"
  - For "YYYYMMDD_Barcodes.txt":
    - Enter the barcodes in the order they appear from the worklist:
      - BAR001
      - BAR002
- Save the files
- Enter "y" into the terminal to proceed

The script will then:

- Generate a printout for today's binding, including the ligands, ligand volumes, pellets, and buffers necessary
- The Radioactivity Archive sheet will open, with today's plates entered at the bottom of the sheet
- Write to the Google Sheet logs for pellets & hot ligands used

### Trouble Shooting

**Ensure the "Radioactive_Archive.xlsx" sheet is saved and closed before entering "y" to proceed, the script will crash otherwise**
Check the log file in the "archive" directory with today's date to get some diagnostic help, such as determining if the number of plates and number of barcodes don't match, if a receptor could not be matched in the database, if there is no current hotligand, etc.

If the script ran, but a mistake was made, the following can be done to undo the changes:

1. Delete the entries added to Hotligand Log and Pellet Log on the Google Sheet
2. Delete the entries added to the bottom of the "Radioactive_Archive.xlsx" sheet
3. If you're concerned about row color formatting, in the "user_config.json" change the "gray_switch" value to:
    1. "true" (exactly undercase) to have the rows be gray
    2. "false" (exactly undercase) to have the rows be white

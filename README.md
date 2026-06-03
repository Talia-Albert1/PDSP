# PDSP Lab Automation

Information and onboarding relevant to PDSP lab data workflows.

* **\procedures:** Contains the `.tex` and `.md` source files, as well as compiled PDFs of lab procedures.
* **\Python_Scripts:** Houses various Python utility scripts. The primary production script is `Binding_Worksheet.py`, located in the `Radioligand_Binding` directory.

---

## Installation & Setup

### 1. Programs

1. Download and install the latest version of **Python**: [python.org/downloads](https://www.python.org/downloads/)
2. Download and install **GitHub Desktop**: [desktop.github.com](https://desktop.github.com/)
3. Clone this repository to your local machine using the GitHub Desktop application.

### 2. Package Installation

To install the required dependencies, navigate to your cloned repository folder and **double-click the `install_packages.py` file**.

#### Alternative: Manual Terminal Installation (If the script fails)

If the automated installer fails, you can install the packages manually via the Windows Command Prompt:

1. Press the **Windows Key**, type `cmd`, and press **Enter**.
2. Run the following command to navigate to the script directory:

    ```bash
    cd /PDSP/Python_Scripts/Radioligand_Binding/
    ```

3. Enter the following command, after navigating to "Radioligand_Binding" directory.

    ```bash
    py -m pip install -r requirements.txt
    ```

## Google Cloud Project Setup

To allow Python to read and write to our shared Google Sheets, every lab member needs a unique service account and JSON token. If you create a new project, ensure that the following API's are enabled.

* Google Drive API
* Google Sheets API

### 1. Access the Cloud Project

* Go to the Google Cloud Console: [console.cloud.google.com](https://console.cloud.google.com/)
* Ensure you are using the shared PDSP Google Account and select the project: **PDSP-Google-Sheet-Writer**.
* *Reference Guide:* [developers.google.com/workspace/guides/create-project](https://developers.google.com/workspace/guides/create-project)

### 2. Add a New User (Service Account)

1. Open the left-hand **Menu** > **IAM & Admin** > **Service Accounts**.
2. Click **+ Create Service Account** at the top.
3. Name the account using the format: `Name-pdsp-writer` and click through to finish.

### 3. Generate and Save JSON Tokens

1. Click on your newly created service account email from the list.
2. Navigate to the **Keys** tab.
3. Click **Add Key** > **Create New Key** > Select **JSON** > Click **Create**.
4. A file will download automatically. Move and rename this file into the script's data directory:
   `/PDSP/Python_Scripts/Radioligand_Binding/data_files/token_name.json`

### 4. Authorize the Service Account on Google Sheets

Copy the unique, automated email address of your new service account (e.g., `Name-pdsp-writer@...iam.gserviceaccount.com`). Open the master Google Sheet, click **Share** in the top right, paste the email, and grant it **Editor** permissions.

---

## How to Use the Script

1. **Double-click `Binding_Worksheet.py`** to start. A terminal window will open.
2. *First-time setup only:* You will be prompted to enter your name, initials, and select your specific Google Sheet JSON token.
3. Two empty text files (`YYYYMMDD_Worklist.txt` and `YYYYMMDD_Barcodes.txt`) will automatically open:
    * **For `YYYYMMDD_Worklist.txt`:** Populate this with the binding type, a tab space, and the plate name. (Note: Copying and pasting directly from Google Sheets formats this automatically).
        * *Example:* `PRIM[tab]receptor-XX` or `SEC[tab]receptor-XX`
    * **For `YYYYMMDD_Barcodes.txt`:** Enter the barcodes in the exact order they appear in your worklist.
        * *Example:* `BAR001` then `BAR002` on the next line.
4. Save and close both text files.
5. Return to the terminal and type `y`, then press **Enter** to proceed.

### What the script does automatically

* Generates a printable daily breakdown (ligands, volumes, pellets, and necessary buffers).
* Appends today's plate data to the bottom of the local `Radioactive_Archive.xlsx` sheet.
* Updates the Google Sheet logs for total pellets and hot ligands used.

---

## Troubleshooting & Undoing Mistakes

**CRITICAL: Ensure the `Radioactive_Archive.xlsx` file is completely closed before typing "y" to run the script.** If the file is open in Excel, the script will crash due to a permission lock.

* **Logs:** If the script encounters an error, check the dated log file inside the `/archive` directory to diagnose issues (e.g., mismatched plate/barcode counts, missing database receptors, or an unassigned hot ligand).
* **Reverting Run Errors:** If the script ran successfully but you realized an error was made in the data input, manually undo it by:
    1. Deleting the wrong rows from the **Hotligand Log** and **Pellet Log** on the master Google Sheet.
    2. Deleting the newly appended rows from the bottom of your local `Radioactive_Archive.xlsx` sheet.
    3. To fix row alternating color formatting bugs, open `/PDSP/Python_Scripts/Radioligand_Binding/user_config.json` and adjust the `"gray_switch"` property:
        * Set to `"true"` (all lowercase letters) to make the next row background gray.
        * Set to `"false"` (all lowercase letters) to make the next row background white.

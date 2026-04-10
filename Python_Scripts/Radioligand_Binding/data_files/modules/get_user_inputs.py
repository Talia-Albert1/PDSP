import tkinter as tk
from tkinter import messagebox
import pandas as pd

def get_user_inputs():
    """Opens a GUI to collect barcodes and worklist entries with validation.
    
    Returns:
        tuple: (barcodes_df, worklist_df) as DataFrames, or
            (None, None) if user cancels.
    """
    root = tk.Tk()
    root.title("Radioligand Binding Setup")
    root.resizable(False, False)
    result = {'barcodes': None, 'worklist': None}

    # ── Barcodes ──────────────────────────────────────────
    barcodes_label = tk.Label(root, text="Barcodes (one per line):", font=('Arial', 11, 'bold'))
    barcodes_label.grid(row=0, column=0, padx=10, pady=(10,2), sticky='w')
    barcodes_box = tk.Text(root, height=12, width=25)
    barcodes_box.grid(row=1, column=0, padx=10, pady=5)

    # ── Worklist ───────────────────────────────────────────
    worklist_label = tk.Label(root, text="Worklist (paste from Google Sheet):", font=('Arial', 11, 'bold'))
    worklist_label.grid(row=0, column=1, padx=10, pady=(10,2), sticky='w')
    worklist_box = tk.Text(root, height=12, width=35)
    worklist_box.grid(row=1, column=1, padx=10, pady=5)

    # ── Validation ─────────────────────────────────────────
    def parse_barcodes(raw):
        """Parse and validate barcode input.
        
        Args:
            raw (str): Raw text from the barcodes input box.
            
        Returns:
            tuple: (list of barcodes, error message or None)
        """
        # get non-empty lines
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        
        # ensure input is not empty
        if not lines:
            return None, "Barcodes cannot be empty."
        
        # check for duplicates
        if len(lines) != len(set(lines)):
            dupes = [b for b in lines if lines.count(b) > 1]
            return None, f"Duplicate barcodes found: {', '.join(set(dupes))}"
        
        return lines, None

    def parse_worklist(raw):
        """Parse and validate worklist input.
        
        Args:
            raw (str): Raw text from the worklist input box.
            
        Returns:
            tuple: (list of (binding_type, plate_name) tuples, error message or None)
        """
        # get non-empty lines
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        
        # ensure input is not exmpty
        if not lines:
            return None, "Worklist cannot be empty."
        
        entries = []
        for i, line in enumerate(lines, start=1):
            columns = line.split('\t')
            
            # must have exactly 2 columns
            if len(columns) != 2:
                return None, (
                    f"Row {i} has {len(columns)} column(s), expected 2.\n"
                    f"Problematic row: '{line}'\n\n"
                    f"Make sure you are pasting directly from the Google Sheet."
                    f"If manually entering, separate columns with tab"
                )
            
            binding_type, plate_name = columns[0].strip(), columns[1].strip()
            
            # binding type must be PRIM or SEC
            if binding_type.upper() not in ('PRIM', 'SEC'):
                return None, (
                    f"Row {i} has an invalid binding type: '{binding_type}'.\n"
                    f"Expected 'PRIM' or 'SEC'."
                )
            
            entries.append((binding_type.upper(), plate_name))
        
        return entries, None

    def validate_plate_barcode_count(barcodes, worklist_entries):
        """Check that barcode count matches expected plate count.
        
        Args:
            barcodes (list): List of barcode strings.
            worklist_entries (list): List of (binding_type, plate_name) tuples.
            
        Returns:
            str or None: Error message, or None if valid.
        """
        prim_count = sum(1 for bt, _ in worklist_entries if bt == 'PRIM')
        sec_count = sum(1 for bt, _ in worklist_entries if bt == 'SEC')
        expected = prim_count + (sec_count * 3)
        actual = len(barcodes)
        
        if expected != actual:
            return (
                f"Barcode count mismatch.\n"
                f"Worklist expects {expected} barcodes "
                f"({prim_count} PRIM barcodes + {sec_count * 3} SEC barcodes.\n"
                f"({sec_count} SEC sets × 3 barcodes per SEC set = {sec_count * 3} SEC barcodes)\n"
                f"You entered {actual} barcodes."
            )
        return None

    def on_submit():
        barcodes_raw = barcodes_box.get("1.0", tk.END)
        worklist_raw = worklist_box.get("1.0", tk.END)

        # validate barcodes
        barcodes, error = parse_barcodes(barcodes_raw)
        if error:
            messagebox.showerror("Barcode Error", error)
            return

        # validate worklist
        worklist_entries, error = parse_worklist(worklist_raw)
        if error:
            messagebox.showerror("Worklist Error", error)
            return

        # validate counts match
        error = validate_plate_barcode_count(barcodes, worklist_entries)
        if error:
            messagebox.showerror("Count Mismatch", error)
            return

        # all good — build dataframes
        result['barcodes'] = pd.DataFrame(barcodes, columns=["Barcode"])
        result['worklist'] = pd.DataFrame(worklist_entries, columns=["Binding Type", "Plate Name"])
        root.destroy()

    def on_cancel():
        root.destroy()

    tk.Button(root, text="Submit", width=15, command=on_submit).grid(
        row=2, column=0, pady=10)
    tk.Button(root, text="Cancel", width=15, command=on_cancel).grid(
        row=2, column=1, pady=10)

    root.mainloop()

    if result['barcodes'] is None or result['worklist'] is None:
        return None, None
    return result['barcodes'], result['worklist']
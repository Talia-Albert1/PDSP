import logging

import pandas as pd
import numpy as np
import datetime
logger = logging.getLogger(__name__)

# "column index in excel":"column name in our dataframe"
COLUMN_MAPPING = {
    1 :"Binding Type",
    2 :"Plate Name",
    3 :"Date",
    4 :"Barcode 0",
    5 :None,#plate_number
    6 :None,#submission_confirm
    7 :"Barcode 1",
    8 :None,#plate_number
    9 :None,#submission_confirm
    10:"Barcode 2",
    11:None,#plate_number
    12:None,#submission_confirm
    13:None,#pellet_book_confirm
    14:None,#ligand_book_confirm
    15:None,#actual_counts
    16:None,#worklist_confirmation
    17:"Receptor",
    18:"Ligand",
    19:"Radionuclide",
    20:"Inventory Control Number",
    21:"Specific Activity",
    22:"Assay Conc",
    23:None,#actual_counts,
    24:"Reference",
    25:"Number of Plates",
    26:"Number of Pellets",
    27:"Buffer Volume",
    28:"uL for Assay",
    29:"uCi/uL Ratio",
    30:"uCi for Assay",
    31:None,#sink_disposal
    32:None,#dry_waste
    33:"Assay BB",
    34:"Filter Type",
    35:"Unifilter Pellet Ratio",
    36:"Filtermat Pellet Ratio",
    37:"Pellets in Inventory",
    38:"Decay Factor"
}

def write_archive_excel():
    print("hi")
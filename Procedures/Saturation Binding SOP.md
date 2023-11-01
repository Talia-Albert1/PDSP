# Saturation Binding Assay
## Protein Concentration
1. Resuspend pellet in 12 mL Lysis Buffer (10mM Tris + 5% Sucrose, pH 7.4):
    - Use 1 mL Lysis Buffer to break up pellet
    - Fill to ~12 mL with Lysis Buffer
    - Pool pellets into one tube (if multiple pellets)
2. Perform Bradford Protein Concentration Assay:
    - Sample Preparation:
        - 10 uL Pellet Suspension + 790 uL dH20 + 200 uL Bradford Reagent
    - Blank Preparation:
        - 10 uL Lysis Buffer + 790 uL dH20 + 200 uL Bradford Reagent
    - Incubate @ RT 10 min
    - Measure absorbance @ 595 nm
    - Calculate protein concentration (Refer to Formulas section or Spreadsheet)

## Hot Ligand Addition
3. Prepare ~15 mL BB (Binding Buffer) w/BSA (~30 uL)
4. In an empty 96-well shallow plate (Need one column):
    1. Add **330 uL** BB to well H and **165 uL** BB to well A-G
    2. Add 3H-Ligand to Well H (Refer to Formulas section or Spreadsheet)
    3. Perform a Serial Dilution (1:2) of **165 uL** up from well H to A
    4. Remove **25 uL** from Well A for radioactivity counts
    5. Using a multichanel pipettor, Transfer **25 uL** into 6 columns of the Drug Plate

## Cold Ligand Addition
5. Add **25 uL** BB to first 3 columns
6. Prepare Cold Ligand (Reference):
    1. Usually, add **4 uL** Reference compound into **800 uL** BB into an eppendorf tube
    2. Using a single channel pipettor, add **25 uL** Reference Compound into the last 3 columns

## Membrane Addition
7. Prepare ~4 mL membrane receptor:
    1. Add BB to trough
    2. Add protein to trough
    3. Using a multichannel pipettor, add **75 uL** protein dilution into all 6 columns
8. Incubate plates @ RT for 1 hour in drawer

## Filtering

## Formulas
Final Volume in each well is **125 uL**
- 25 uL 3H Hot Ligand
- 25 uL Binding Buffer/Cold Ligand (Reference)
- 75 uL Membrane

### Protein concentration
Need:
- OD @ 595 nm
$$\text{Protein Concentration (ug/uL)} = \frac{\text{OD@595 nm} - 0.094}{0.503}$$
Where:
- 0.094 and 0.503 were determined from experimental procedure, provided by XP.

### 3H Hot Ligand
Need:
- Starting Concentration (nM)
- 3H-Ligand Specific Activity (Ci/mmol)
$$\text{3H-Ligand Vol (uL)} = \frac{ 330 \text{ (uL) } * \text{Starting Concentration (nM)} * 5 * 1.2}{ \text{Specific Activity (Ci/mmol)}^{-1} * 1000000}$$
Where:
- 330 uL is double the volume of 165 uL, (25 uL * 6 wells * 1.1 overage = 165 uL), so we can perform a serial dilution
- 5 is a Dilution Factor, the final volume in each well is 125 uL, we add 25 uL from the Hot-Ligand plate, (125/25=5)
- 1.2 is a 20% overage
- 1000000 is for unit conversion

### Cold Ligand
Usually need **4 uL** Reference compound and **800 uL** BB

Need:
- Concentration of Cold Ligand (Reference) Stock (most are 10 mM)
$$\text{Reference Vol (uL)} = \frac{800 \text{ uL} * 10 \text{ uM Final Concentration} * 5}{10000 \text{ uM Starting Concentration}}$$
Where:
- 800 uL is approixmate volume we need (8 Wells/Column * 3 Columns * 25 uL/Well * 1.1 overage = 660), use 800 so pulling from reference is easier
- Final concentration of Cold Ligand (Reference) in each well is 10 uM
- 5 is a Dilution Factor, the final volume in each well is 125 uL, we add 25 uL from the Hot-Ligand plate, (125/25=5)
- 10000 uM or 10 mM is starting reference concentration, usually

### Membrane Receptor
Need:
- Protein Concentration (ug/uL) (Determined previously)
- Protein/Well (ug) (XP will provide this)
$$\text{Volume of Protein (uL)} = \frac{\text{Protein/Well (ug)} * 4000 \text{ uL}}{ \text{Protein Concentration (ug/uL)} * 75 \text{ uL}}$$
$$\text{Volume of BB (uL)} = 4000 \text{ uL} - \text{Volume of Protein (uL)}$$
Where:
- 75 uL is the volume that will be dispensed into each well
- 4000 uL is approixmate volume we need (8 Wells/Column * 6 Columns * 75 uL/Well * 1.1 overage = 3960 uL), round to 4000 uL for convience

### Determining Starting Concentration
After obtaining actual radioactive counts (dpm) starting concentration (concentration of 3H-Ligand in Well H) can be determined.

Need:
- Specific Activity (Ci/mmol)
- Actual Counts (dpm)
$$\text{Starting Concentration (nM)} = \frac{\text{Actual Counts (dpm)} * 10^9 \text{ nM/M} * 2^7}{2.22*10^{12} \text{ dpm/Ci} * \text{Specific Activity (Ci/mmol)} * 0.125 \text{ mL/Well}}$$
Where:
- $10^9$ in a unit conversion to nM from M
- $2^7$ is for the 7 serial 1:2 dilutions
- $2.22*10^{12} \text{ dpm/Ci}$ is a constant
- 0.125 mL/Well is the final volume in each well
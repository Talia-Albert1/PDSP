# Saturation Binding Assay
## Protein Concentration
1. Resuspend pellet in 12 mL Lysis Buffer (10mM Tris + 5% Sucrose, pH 7.4):
    - Use 1 mL Lysis Buffer to break up pellet
    - Fill to ~12 mL
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

## Cold Ligand Addition

## Membrane Addition

## Filtering

## Formulas
Final Volume in each well is **125 uL**
    - 25 uL Hot Ligand
    - 25 uL Binding Buffer/Cold Ligand (Reference)
    - 75 uL Membrane

### Protein concentration
Need:
- OD @ 595 nm
$$\text{Protein Concentration (ug/uL)} = \frac{\text{OD@595 nm} - 0.094}{0.503}$$
Determined from experimental procedure, equation provided by XP.

### Hot Ligand
Need:
- Starting Concentration (nM)
- 3H-Ligand Specific Activity (Ci/mmol)
$$\text{3H-Ligand Vol (uL)} = \frac{330 \text{ (uL) * \text{Starting Concentration (nM)} * 5 * 1.2}}{\text{Specific Activity (Ci/mmol)}^{-1}*1000000}$$

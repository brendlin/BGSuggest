
BGSuggest
====================

Extract the data
--------------

The data must be extracted and converted to a root ttree.

To be filled in.

Study the data: "python Improve.py"
--------------

**Improve.py** is the portal script for making plots.

### Options

The following options correspond to the types of studies / plots you can make / do:

 - **--yir**: year-in-review plots, or average and standard deviation of BG, as well as A1c plots.
 - **--overview**: One-week overview of BG values
 - **--detailed**: One-day detailed look at BGs, CGM readings, insulin delivered, and food eaten. Includes a predictive curve based on the BolusWizard calculation.
 - **--isig:** Study the MARD of the CGM readings

Other options:

 - **--week**: Which week to study (used by --overview and --detailed)
 - **--m** (or t, w, th, f, s, su): which day (of the week specified) to study in detail (used by --detailed)
 - **--today** picks today's date to look at in detail.
 - **--save** (saves the pdfs)

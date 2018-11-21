centrifugation_expt
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/centrifugation_expt.png)](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/centrifugation_expt)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/REPLACE_WITH_APPVEYOR_LINK/branch/master?svg=true)](https://ci.appveyor.com/project/REPLACE_WITH_OWNER_ACCOUNT/centrifugation_expt/branch/master)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/centrifugation_expt/branch/master/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/centrifugation_expt/branch/master)

Calculate and plot analyzed data from centrifugation experiment

### To use with csv data file
    
 Calculations and plots created by program **data_proc.py** in **centrifugation_expt** folder within main project directory. 
 
 "data_proc -c *file location*" allows reading in of csv file. csv data file format must be as follows, all masses are in *grams*:
 
 time of last solvent addition (mo/d/yr hr:min), mass of empty solution vial, mass of vial + oil, mass of vial + oil + solvent
 time of centrifugation (mo/d/yr hr:min), mass of empty tube, mass of tube + liquid, mass of tube + dried cake
 (repeat row 2 as necessary)
 
 Program returns statements in the terminal that files were written and two files, one with a plot of the analyzed data 
 and another with the data in a csv file. The data written in the csv file file is organized in columns of 
 **aging time (hrs), aging time (sec), and concentration of dried cake (g/g oil)**, respectively.
 
 ### To use with excel data file
     
  Calculations and plots created by program **data_proc.py** in **centrifugation_expt** folder within main project directory. 
  
  "data_proc.py -e *file location*" allows reading in of excel file. excel data file format must be as follows, all masses are in *grams*:
  
  Each sheet contains 1 set of the following data. Changing sheet names is optional and does not affect the program:
  
  8 columns as follows: (A) time of last solvent addition (mo/d/yr hr:min), (B) mass of empty solution vial, (C) mass of vial + oil, 
  (D) mass of vial + oil + solvent, (E) time of centrifugation (mo/d/yr hr:min), (F) mass of empty tube, (G) mass of tube + liquid, 
  (H) mass of tube + dried cake
  
  The first four columns each only contain one row. The columns (E) through (H) should contain as many rows as there are
  data points studied.
  
  Program returns statements in the terminal that files were written, and two files, one with a plot of the analyzed data 
  and another with the data in a excel file. The data written in the excel file file is organized in columns of 
  **aging time (hrs), aging time (sec), and concentration of dried cake (g/g oil)**, respectively. Each analyzed data 
  set is written to the same sheet number that it was read in from.

### Copyright

Copyright (c) 2018, kachj


#### Acknowledgements
 
Project based on the 
[Computational Chemistry Python Cookiecutter](https://github.com/choderalab/cookiecutter-python-comp-chem)

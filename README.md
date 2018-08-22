# InitialiseModelica
This script reads data from Matpower results and initialises OpenIPSL based Modelica models with Matpower power flow data

## Requirements
The script needs Numpy and Scipy libraries to run. It takes the test.mo file to be initialised as input, the matlab test.mat result file generated from Matpower to create a test_modified.mo file at the same location as the test.mo file.
  
## Usage
To use the script, do the following:  

- Download the matModelica.py file.
- From terminal, use  
`python /path/to/matModelica.py "path/to/modelica/file.mo" "path/to/result/file.mat"`

## Modelica model format
The script will work only if the Modelica model is in a required format. For proper working, the following rules must be adhered to to properly initialise the Modelica OpenIPSL models:

  - Loads must be named in an alphanumeric fashion, like: **Load1**. Here, the name must be **Load** (case insensitive) and the number must correspond to the bus to which the load is connected.
  - Similarly for generators, all the generators must be named alphanumerically, such as **Gen1** (case insensitive), with numeric part corresponding to the bus number.
  - Model topology must be same in Matpower and Modelica.
  

The current scipt has been tested with modelica models created using OpenIPSL library and OpenModelica. Matpower with MATLAB 2016 was used to run power flows on corresponding system.

## Copyrights
Copyright August 2018 - current [Digvijay Gusain](https://www.tudelft.nl/staff/d.gusain/), [Intelligent Electrical Power Grids, Delft University of Technology, The Netherlands](https://www.tudelft.nl/en/eemcs/the-faculty/departments/electrical-sustainable-energy/intelligent-electrical-power-grids-iepg-group/).
The author can be contacted by email: d.gusain@tudelft.nl. This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0.

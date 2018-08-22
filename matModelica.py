# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 19:16:37 2018

@author: digvijaygusain
"""

import numpy as np
import re
import sys, os

arguments = sys.argv
modelicaFile, matlabFile = arguments[1], arguments[2]

file_path = os.path.dirname(os.path.abspath(modelicaFile))
modelica_model_name = modelicaFile.replace(file_path,'').split('.')[0][1:]+'_modified.mo'
modified_file_path = os.path.join(file_path,modelica_model_name)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#the following has been taken from StackOverflow answer:
# https://stackoverflow.com/a/8832212

import scipy.io as spio

def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict_):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict_:
        if isinstance(dict_[key], spio.matlab.mio5_params.mat_struct):
            dict_[key] = _todict(dict_[key])
    return dict_        

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict_ = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict_[strg] = _todict(elem)
        else:
            dict_[strg] = elem
    return dict_

#This has been developed by @dgusain1
def check_regex(testString):
    #print(testString)
    voltage_regex = r'V_0\s?=\s?\d\.\d*'
    angle_regex = r'angle_0\s?=\s?-?\d+[\.\d*]*'#|\d+\.\d*]'
    name_regex = r'\w+\s\w+'
    Q_regex = r'Q_0\s?=\s?\d+[\.\d*]*'
    
    voltage = re.findall(voltage_regex, testString)[0].split(' = ')[1]
    angle = re.findall(angle_regex, testString)[0].split(' = ')[1]
    name = re.findall(r'([A-Za-z]+)(\d+)',re.findall(name_regex, testString)[0])
    
    if len(name)>1:
        name = name[1]
    else:
        name = name[0]
    try:
        q = re.findall(Q_regex, testString)[0].split(' = ')[1]
    except IndexError:
        q='0'
    
    return [name, voltage, angle, q]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#matlabFile = r'D:\digvijaygusain\Desktop\result.mat'

#load matlab results file
print("Loading matlab result file...")
matResult = loadmat(matlabFile)

print("Organizing results..")
#get results for bus and gen
busResults = matResult['results']['bus']
genResults = matResult['results']['gen']
genBuses = [int(x[0]) for x in genResults if x[1] !=0]

#create array for all bus voltages
busVoltagesTemp = [(int(x[0]), x[7], x[8]) for x in busResults]
busVoltages = np.array(busVoltagesTemp, dtype=[('bus',np.int),('voltage',np.float),('angle',np.float)])

#Similarly create arrays for generators
#variables are: bus number, voltage, angle, and Q_0
temp = [(int(x[0]), x[2]) for x in genResults]
genVariables = np.array(temp, dtype=[('bus',np.int),('Q_0',np.float)])  #,('voltage',np.float),('angle',np.float)


#input the *.mo file to be changed
#modelicaFile = r'C:\Users\digvijaygusain\OneDrive\TU_Delft\PhD\Teaching Assistantship\IEPG_Course_2019\Models\14 bus with wind\IEEE14Bus.mo'
print("Initialising %s.mo.." %(modelica_model_name[:-12]))
with open(modelicaFile) as infile, open(modified_file_path, 'w') as outfile:
    for line in infile:
        try:
            info = check_regex(line)
            (name, bus) = info[0]
            voltage = list(busVoltages['voltage'])[list(busVoltages['bus']).index(int(bus))]
            angle = list(busVoltages['angle'])[list(busVoltages['bus']).index(int(bus))]
            line = line.replace(info[1], str(voltage))
            if info[2] == '0':
                to_replace = 'angle_0 = 0'
                replace_to = 'angle_0 = '+str(angle)
                line = line.replace(to_replace, replace_to)
            else:
                line = line.replace(info[2], str(angle))
            if name.lower() == 'gen':
                Q_0 = list(genVariables['Q_0'])[list(genVariables['bus']).index(int(bus))]
                if info[3] == '0':
                    to_replace = 'Q_0 = 0'
                    replace_to = 'Q_0 = '+str(Q_0)
                    line = line.replace(to_replace, replace_to)
                else:
                    line = line.replace(info[3], str(Q_0))
        except IndexError:
            pass
        

        outfile.write(line)
print('Done..')


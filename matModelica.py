# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 19:16:37 2018

@author: digvijaygusain
"""

#from lxml import etree
#from fmpy.model_description import ScalarVariable
#from scipy.io import loadmat
import numpy as np
import re

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

def check_regex(testString):
    #print(testString)
    voltage_regex = r'V_0\s?=\s?\d\.\d*'
    angle_regex = r'angle_0\s?=\s?-?\d+[\.\d*]*'#|\d+\.\d*]'
    name_regex = r'\w+\s\w+'
    Q_regex = r'Q_0\s?=\s?\d+[\.\d*]*'
    
    voltage = re.findall(voltage_regex, testString)[0].split(' = ')[1]
    angle = re.findall(angle_regex, testString)[0].split(' = ')[1]
    name = re.findall(r'([A-Za-z]+)(\d+)',re.findall(name_regex, testString)[0])
    #print(name)
    if len(name)>1:
        name = name[1]
    else:
        name = name[0]
    try:
        q = re.findall(Q_regex, testString)[0].split(' = ')[1]
    except IndexError:
        q='0'
    
    #print([name, voltage, angle, q])
    return [name, voltage, angle, q]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#xmlFile = r'C:\Users\digvijaygusain\AppData\Local\Temp\OpenModelica\OMEdit\IEEE14BusWind_init.xml'
matlabFile = r'D:\digvijaygusain\Desktop\result.mat'

#load matlab results file
matResult = loadmat(matlabFile)

#get results for bus and gen
busResults = matResult['results']['bus']
genResults = matResult['results']['gen']
genBuses = [int(x[0]) for x in genResults if x[1] !=0]

#create array for all bus voltages
busVoltagesTemp = [(int(x[0]), x[7], x[8]) for x in busResults]
busVoltages = np.array(busVoltagesTemp, dtype=[('bus',np.int),('voltage',np.float),('angle',np.float)])

#Create array for loads
#loads must be named in sequence with their bus numbers
#variables taken into account are Bus number, V_0, angle_0
#temp = [(int(x[0]), x[7], x[8]) for x in busResults if x[2] != 0]
#loadVariables = np.array(temp, dtype=[('bus',np.int),('voltage',np.float),('angle',np.float)])

#Similarly create arrays for generators
#variables are: bus number, voltage, angle, and Q_0
temp = [(int(x[0]), x[2]) for x in genResults]
#temp1 = []
#for item in temp:
#    index = list(busVoltages['bus']).index(item[0])
#    temp1.append((item[0],busVoltages[index][1],busVoltages[index][2],item[1]))
genVariables = np.array(temp, dtype=[('bus',np.int),('Q_0',np.float)])  #,('voltage',np.float),('angle',np.float)


#input the *.mo file to be changed
modelicaFile = r'C:\Users\digvijaygusain\OneDrive\TU_Delft\PhD\Teaching Assistantship\IEPG_Course_2019\Models\14 bus with wind\IEEE14Bus.mo'
with open(modelicaFile) as infile, open(r'C:\Users\digvijaygusain\OneDrive\TU_Delft\PhD\Teaching Assistantship\IEPG_Course_2019\Models\14 bus with wind\IEEE14Bus_modified.mo', 'w') as outfile:
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
        


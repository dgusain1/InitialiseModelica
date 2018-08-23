# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 19:16:37 2018

@author: digvijaygusain
"""

import numpy as np
import re
import sys, os
from time import sleep

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
    '''
    This function checks each line of Modelica model code and identified loads and generators.
    Also identifies the voltages, angles (for loads and gens) and reactive powers (for generators only) to be replaced/updated.    
    '''
    #print(testString)
    voltage_regex = r'V_0\s?=\s?\d[\.\d*]*'
    angle_regex = r'angle_0\s?=\s?-?\d+[\.\d*]*'#|\d+\.\d*]'
    name_regex = r'\w+\s\w+'
    P_regex = r'P_0\s?=\s?\d+[\.\d*]*'
    Q_regex = r'Q_0\s?=\s?\d+[\.\d*]*'
    
    voltage = re.findall(voltage_regex, testString)[0].split(' = ')[1]
    angle = re.findall(angle_regex, testString)[0].split(' = ')[1]
    name = re.findall(r'([A-Za-z]+)(\d+)',re.findall(name_regex, testString)[0])
    
    if len(name)>1:
        name = name[1]
    else:
        name = name[0]
    try:
        p = re.findall(P_regex, testString)[0].split(' = ')[1]
        q = re.findall(Q_regex, testString)[0].split(' = ')[1]
    except IndexError:
        p, q = '0', '0'
#    print([name, voltage, angle, q])
    return [name, voltage, angle, p, q]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#load matlab results file
#print("Loading matlab result file...")
matResult = loadmat(matlabFile)

#print("Organizing results..")
#get results for bus and gen
busResults = matResult['results']['bus']
genResults = matResult['results']['gen']
genBuses = [int(x[0]) for x in genResults if x[1] !=0]

#create array for all bus voltages
busVoltagesTemp = [(int(x[0]), x[7], x[8], x[2], x[3]) for x in busResults]
busVoltages = np.array(busVoltagesTemp, dtype=[('bus',np.int),('voltage',np.float),('angle',np.float), ('P_0',np.float),('Q_0',np.float)])

#Similarly create arrays for generators
#variables are: bus number, voltage, angle, and Q_0
temp = [(int(x[0]), x[1], x[2]) for x in genResults]
genVariables = np.array(temp, dtype=[('bus',np.int),('P_0',np.float),('Q_0',np.float)])  #,('voltage',np.float),('angle',np.float)

def replacement(prefix, infoVal, replacedVal, line):
    
    to_replace = prefix+'_0 = '+infoVal
    replace_to = prefix+'_0 = '+str(replacedVal)
#    print('original line:')
#    print(line)
    line = line.replace(to_replace, replace_to)
#    print('changed line:')
#    print(line)
    return line
    
#input the *.mo file to be changed
#print("Initialising %s.mo.." %(modelica_model_name[:-12]))
with open(modelicaFile) as infile, open(modified_file_path, 'w') as outfile:
    for line in infile:
#        print(line)
        try:
            info = check_regex(line)
            (name, bus) = info[0]
            
            voltage = list(busVoltages['voltage'])[list(busVoltages['bus']).index(int(bus))]
            angle = list(busVoltages['angle'])[list(busVoltages['bus']).index(int(bus))]
#            print((name,voltage, info))
#            sleep(2)
            
            if info[1] in '0123':
                line = replacement('V', info[1], voltage, line)
            else:
                line = line.replace(info[1], str(voltage))
                
            if info[2] in '0123':
                line = replacement('angle', info[2], angle, line)
            else:
                line = line.replace(info[2], str(angle))
            
#            
#            if info[1] in '0123':
#                to_replace = 'V_0 = '+info[1]
#                replace_to = 'V_0 = '+str(voltage)
#                line = line.replace(to_replace, replace_to)
#            else:
#                line = line.replace(info[1], str(voltage))
#                
#            
##            print((name,bus, voltage, angle))
#            if info[2] in '0123':
#                to_replace = 'angle_0 = '+info[1]
#                replace_to = 'angle_0 = '+str(angle)
#                line = line.replace(to_replace, replace_to)
#            else:
#                line = line.replace(info[2], str(angle))
            
            
            if name.lower() == 'gen':
                P_0 = list(genVariables['P_0'])[list(genVariables['bus']).index(int(bus))]
                Q_0 = list(genVariables['Q_0'])[list(genVariables['bus']).index(int(bus))]
                if info[3] in '0123':
                    line = replacement('P', info[3], P_0, line)
    #                to_replace = 'Q_0 = '+info[1]
    #                replace_to = 'Q_0 = '+str(Q_0)
    #                line = line.replace(to_replace, replace_to)
                else:
                    line = line.replace(info[3], str(P_0))
                
                if info[4] in '0123':
                    line = replacement('Q', info[4], Q_0, line)
                else:
                    line = line.replace(info[4], str(Q_0))
            
            elif name.lower() == 'load':
                P_0 = list(busVoltages['P_0'])[list(busVoltages['bus']).index(int(bus))]
                Q_0 = list(busVoltages['Q_0'])[list(busVoltages['bus']).index(int(bus))]
                if info[3] in '0123':
                    line = replacement('P', info[3], P_0, line)
                else:
                    line = line.replace(info[3], str(P_0))
                
                if info[4] in '0123':
                    line = replacement('Q', info[4], Q_0, line)
                else:
                    line = line.replace(info[4], str(Q_0))
#            print('\n\n\n')
            print('Initialised element: %s..' %(name+bus))
        except Exception as e:
#            print(e)
#            sleep(3)
            pass
        
        
        outfile.write(line)
print('Done..')


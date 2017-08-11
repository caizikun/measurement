import io,sys
import numpy as np
import qt
import msvcrt
import copy


SETUP = qt.current_setup

SAMPLE = qt.exp_params['samples']['current']

def write_to_msmt_params_file(search_strings, param_string_overrides,debug,round_decimals=2):
    if not debug:
        with open(r'D:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py','r') as param_file:
            data = param_file.readlines()

        for i in range(len(search_strings)):
            search_string = search_strings[i]
            param_string_override = param_string_overrides[i]

            data = write_to_file_subroutine(data, search_string, param_string_override=param_string_override, round_decimals=round_decimals)

        ### after compiling the new msmt_params, the are flushed to the python file.
        f = open(r'D:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py','w')
        f.writelines(data)
        f.close()


def write_to_file_subroutine(data,search_string,param_string_override=None,round_decimals=2):
    """
    Takes a list of read file lines and a search string.
    Scans the file for uncommented lines with this specific string in it.
    It is assumed that the string occurs within the dictionary part of msmt_params.
    Beware: Will delete any comments attached to the specific parameter.
    """

    ## get the calibrated value
    params = qt.exp_params['samples'][SAMPLE][search_string]

    ### correct file position (makes sure that we do not overwrite parameters for the wrong sample.
    ### is also used to break the loop when we have looped over the sample
    correct_pos = False

    for ii,x in enumerate(data):

        ### check if we write params to the correct sample.

        if 'samples' in x and (SAMPLE in x or 'name' in x): ## 'name added for the msmt params of lt3'
            correct_pos = True
        elif 'samples' in x and (not SAMPLE in x or not 'name' in x): ## 'name added for the msmt params of lt3'
            correct_pos = False

        ### write params to sample
        if search_string in x and not '#' in x[:5] and correct_pos:
            if not param_string_override is None:
                array_string = param_string_override+',\n'
            ### detect if we must write a list to the msmt_params or an integer
            elif type(params) == list or type(params) == np.ndarray:
                array_string = 'np.array('

                for i,phi in enumerate(params):
                    if i+1 == len(params):
                        array_string += '['+str(round(phi,round_decimals))+']),\n'

                    else:
                        array_string += '['+str(round(phi,round_decimals))+'] + '

            else:
                array_string = str(round(params,round_decimals))+',\n'


            ## search for the colon in the dictionary and append the numpy array to the string.
            fill_in = x[:x.index(':')+1] + ' '+ array_string

            # print fill_in
            data[ii] = fill_in

            # print 'this is the string I am looking for', search_string
            # print 'this is what i write', data[ii]

    ### return the contents of msmt_params.py
    return data

def write_etrans_param_to_msmt_params_file(var_name, trans, new_value, debug):
    if not debug:
        with open(r'D:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py','r') as param_file:
            data = param_file.readlines()

        data = write_etrans_param_to_file_subroutine(data, var_name, trans, new_value)

        ### after compiling the new msmt_params, the are flushed to the python file.
        f = open(r'D:/measuring/measurement/scripts/'+SETUP+'_scripts/setup/msmt_params.py','w')
        f.writelines(data)
        f.close()

def write_etrans_param_to_file_subroutine(data, var_name, trans, new_value, raise_if_not_found=True):
    correct_pos = False
    correct_pos_found = False
    correct_lines_found = 0

    for ii,x in enumerate(data):
        p1_found = False
        m1_found = False
        ### check if we write data to the right electron transition
        if "electron_transition == '+1':" in x:
            p1_found = True
        elif "electron_transition == '-1':" in x:
            m1_found = True

        if p1_found or m1_found:
            if (p1_found and trans == '_p1') or (m1_found and trans == '_m1'):
                correct_pos = True
                correct_pos_found = True
            else:
                correct_pos = False

        if correct_pos:
            checkstr = var_name + " = "
            if checkstr in x:
                correct_lines_found += 1
                param_column = x.index(checkstr) + len(checkstr)
                fill_in = x[:param_column] + new_value

                data[ii] = fill_in

    print("Correct lines found: %d" % correct_lines_found)
    if (not correct_pos_found or correct_lines_found < 1) and raise_if_not_found:
        raise Exception("The correct position to write parameter variable %s has not been found!" % var_name)
    return data


import qt
import data
from analysis.lib.fitting import fit, common
from analysis.lib.tools import toolbox
from analysis.lib.m2 import m2
from numpy import *
from matplotlib import pyplot as plt
from analysis.lib.tools import plot
import msvcrt
import sce_expm_pq as sce; reload(sce)
import analysis.lib.single_click_ent.SCE_spin_spin_correlators as sce_ssc

def calibrate_MW_phase(plot_corrs = True):

    # run our msmst
    sce.EntangleXcalibrateMWPhase('MWPhaseCalibration')

    phi,phi_u = sce_ssc.calc_MW_phases('MWPhaseCalibration',single_file = True, plot_corrs = plot_corrs)

    if phi_u > 10:
        print 'Phase uncertainty greater than 10 degrees!!!'

    write_to_msmt_params('LDE_final_mw_phase', phi)


def write_to_msmt_params(search_string,val):

    """
    This routine automatically takes the measured values and writes them to the measurement parameters.
    """

    with open(r'D:/measuring/measurement/scripts/single_click_ent/EntExperiment/sce_expm_params_lt4.py','r') as param_file:
        data = param_file.readlines()

        data = write_to_file_subroutine(data,search_string,val)
            
    ### after compiling the new msmt_params, the are flushed to the python file.
    f = open(r'D:/measuring/measurement/scripts/single_click_ent/EntExperiment/sce_expm_params_lt4.py','w')
    f.writelines(data)
    f.close()



def write_to_file_subroutine(data,search_string,val):
    """
    Takes a list of read file lines and a search string.
    Scans the file for uncommented lines with this specific string in it.
    Beware: Will delete any comments attached to the specific parameter.
    """

    for ii,x in enumerate(data):


        ### write params to sample
        if search_string in x:

            array_string = str(round(val,2))+'\n'

            ## search for the colon in the dictionary and append the numpy array to the string.
            fill_in = x[:x.index('=')+1] + ' '+ array_string

            data[ii] = fill_in

    ### return the contents of msmt_params.py
    return data


if __name__ == '__main__':
    calibrate_MW_phase()
"""
PH 2017
Script that attempts to calibrate the phase stabilisation msmt parameters
In practice we didnt use this since they didnt change significantly, and changes implied that we needed to reoptimise our position on the NVs
"""

import qt
import data
from analysis.lib.fitting import fit, common
from analysis.lib.tools import toolbox
from analysis.lib.m2 import m2
from numpy import *
from matplotlib import pyplot as plt
from analysis.lib.tools import plot
import msvcrt
import sce_expm_pq as sce
reload(sce)


def measure_counts():

    #measurement parameters
    steps=21
    counter=2 #number of counter
    Vmax = 4.0

    desired_counts = 5e4

    phase_aom = qt.instruments['PhaseAOM']
    current_adwin = qt.instruments['adwin']
    ZPLServo = qt.instruments['ZPLServo']

    current_adwin.start_counter()
    ZPLServo.move_in() # PH for now we just look at the LT3 counts. Bit of a bodge.

    phase_aom.set_power(0)
    qt.msleep(1)

    V_setpoint = 0.0

    print 'Calibrating PhaseAOM countrate'
    for v in linspace(0,Vmax,steps):
        phase_aom.apply_voltage(v)
        qt.msleep(0.2)
        counts = current_adwin.get_countrates()[counter-1]
        print v, counts
        if (counts > desired_counts):
            V_setpoint = v
            break
    
    if V_setpoint == 0.0:
        print 'Couldn''t get to desired voltage!!!'
        V_setpoint = Vmax

    phase_aom.set_power(0)
    ZPLServo.move_out()
    qt.msleep(1)
    write_to_msmt_params('Phase_Msmt_voltage', V_setpoint)



def measure_g0():

    #measurement parameters
    counter1=2 #number of counter
    counter2=3 #number of counter
    Vset = 4.0

    phase_aom = qt.instruments['PhaseAOM']
    current_adwin = qt.instruments['adwin']
    ZPLServo = qt.instruments['ZPLServo']

    ZPLServo.move_in() # PH for now we just look at the LT3 counts. Bit of a bodge.

    phase_aom.apply_voltage(Vset)
    current_adwin.start_counter()
    qt.msleep(1)

    counts1 = 0
    counts2 = 0

    for v in range(20):
        qt.msleep(0.2)
        counts = current_adwin.get_countrates()
        counts1 += counts[counter1-1]
        counts2 += counts[counter2-1]
        print counts1
        print counts2
    est_g0 = counts1/float(counts2)
    phase_aom.apply_voltage(0.0)
    ZPLServo.move_out()

    print 'Est_g0 ', est_g0
    write_to_msmt_params('Phase_Msmt_g_0', est_g0)



def measure_interferometer(plot_fit = True):

    # run our msmst
    sce.phase_calibration('PhaseStabCalibration')

    folder = toolbox.latest_data('PhaseStabCalibration')

    a = m2.M2Analysis(folder)

    sample_counts_1 = a.g['adwindata']['sampling_counts_1'].value
    sample_counts_2 = a.g['adwindata']['sampling_counts_2'].value

    print 'Avg counts ', np.mean(sample_counts_1), np.mean(sample_counts_2)
    sample_cycles = a.g.attrs['sample_points']
    x = linspace(-a.g.attrs['stretcher_V_max'],a.g.attrs['stretcher_V_max'], sample_cycles)

    g0 = a.g.attrs['Phase_Msmt_g_0']
    rescaled = [n0/(float(n0) + float(n1)*g0) for n0,n1 in zip(sample_counts_1,sample_counts_2)]


    fig = plt.figure(figsize=(17,6))
    ax1 = plt.subplot(212)
    
    ax2 = plt.subplot(211)
    ax1.plot(x,rescaled)
    ax2.plot(x,sample_counts_1,x,sample_counts_2)
    frequency = 1/a.g.attrs['stretcher_V_2pi']
    offset = 0.5
    amplitude = 0.5
    phase = 0

    p0, fitfunc, fitfunc_str = common.fit_cos(frequency,offset, amplitude, phase)
    fit_result1 = fit.fit1d(x,rescaled, None, p0=p0, fitfunc=fitfunc, do_print=True, ret=True)

    ## plot data and fit as function of total time
    if plot_fit == True:
        plot.plot_fit1d(fit_result1, np.linspace(x[0],x[-1],1001), ax=ax1, plot_data=False)

    title = 'analyzed_result'
    plt.ion()
    plt.show()
    plt.savefig(os.path.join(folder, title + '.pdf'),
    format='pdf')
    plt.savefig(os.path.join(folder, title + '.png'),
    format='png')
    
    est_V_2pi = 1.0/(fit_result1['params_dict']['f'])
    print 'Estimated V 2 pi ', est_V_2pi

    est_vis = 1.0/(np.abs(fit_result1['params_dict']['A'] / fit_result1['params_dict']['a']))
    print 'Estimated vis ', 1/est_vis

    # write_to_msmt_params('Phase_Msmt_Vis', est_vis)
    # write_to_msmt_params('stretcher_V_2pi', est_V_2pi)


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
    # measure_g0()
    # measure_counts()
    measure_interferometer()
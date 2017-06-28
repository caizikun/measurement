"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return False
    else:
        return True

def SimpleDecoupling(name,N=4,sweep = 'tau',end=100e-3,nr_list=[1], XY_scheme=8, reps=500,debug=False,larmor_offset = 0):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = reps #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'

    tau_larmor = np.round(1/m.params['C1_freq_0'],9)


    if N==1:
        m.params['Final_Pulse'] ='x'
    else:
        m.params['Final_Pulse'] ='-x'
    ### Calculate tau larmor
    print 'tau_larmor = %s' %tau_larmor
    m.params['tau_larmor_offset'] = larmor_offset

    
    Number_of_pulses = N


    if sweep == 'tau':
        tau_list = np.array([round(x*tau_larmor*0.25e9) / (0.25e9) for x in nr_list]) + larmor_offset
        
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(len(tau_list)).astype(int)
        m.params['tau_list']         = tau_list

    elif sweep == 'N':
        tau_list = 40.32e-6*np.ones(len(nr_list)) + larmor_offset
        m.params['Number_of_pulses'] = nr_list
        m.params['tau_list']         = tau_list

    m.params['pts']              = len(tau_list)
    m.params['sweep_pts']        =  2*m.params['Number_of_pulses']*tau_list*1e3
    m.params['sweep_name']       = 'total evolution time (ms)'
    if XY_scheme == 16:
        m.params['Decoupling_sequence_scheme']='repeating_T_elt_XY16'
    elif XY_scheme == 8:
        m.params['Decoupling_sequence_scheme']='repeating_T_elt'
    elif XY_scheme == 4:
        m.params['Decoupling_sequence_scheme']='repeating_T_elt_XY4'
    else:
        raise Exception('XY Scheme not recognized')
    #m.params['Decoupling_sequence_scheme']='single_block'


    m.autoconfig()
    funcs.finish(m, upload =True, debug=debug)


def take_DD_Data(larmor_min,larmor_max,N,pts,sweep = 'tau',larmor_step=2,larmor_offset = 0, XY_scheme=8, reps=500, debug=False):
    ## loop function for data acquisition.

    Continue_bool = True 

    larmor_steps = pts*larmor_step ### how many steps in in tau_larmor are taken
    nr_of_runs = int(np.floor((larmor_max-larmor_min)/larmor_steps))

    if sweep == 'N':
        sweep_pts_total = np.arange(larmor_min,larmor_max,larmor_step)
        total_no_of_elements = np.sum(sweep_pts_total)*2+5*len(sweep_pts_total)
        nr_of_runs = np.ceil(total_no_of_elements/7500.) ### we want to load 7500 elements per run into the AWG.

    print 'nrofruns', nr_of_runs
    if not qstop(sleep=3):
            Continue_bool = False
    else:
        for n in range(int(nr_of_runs)):
            if not qstop(sleep=3):
                Continue_bool = False
                return False
            print 'n', n

            if sweep == 'tau':
                nr_list = np.arange(larmor_min+n*larmor_steps,larmor_min+(n+1)*larmor_steps,larmor_step)
                sweep_string = '_RepT_XY'+str(XY_scheme)+'_N_'+str(N)+'_part'+str(n+1)
            elif sweep == 'N':
                no_of_elts_per_sweep_pt = sweep_pts_total.copy()*2+5
                nr_list = sweep_pts_total[(np.cumsum(no_of_elts_per_sweep_pt) < 7500)]
                sweep_pts_total = sweep_pts_total[np.logical_not(np.cumsum(no_of_elts_per_sweep_pt)<7500)]
                sweep_string = '_RepT_XY'+str(XY_scheme)+'_tauoff_'+str(larmor_offset*1e9)+'_part'+str(n+1)
            else:
                print 'Unknown sweep variable in electron_T2_slave_script.py'
                return False
            print 'nr_list', nr_list

            SimpleDecoupling(SAMPLE+sweep_string,
                                    N=N,nr_list = nr_list,larmor_offset = larmor_offset,
                                    reps=reps, sweep=sweep,XY_scheme=XY_scheme, debug=debug)

    ### get the remaining larmor revivals in.
    if sweep == 'tau':
        if Continue_bool:
            nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,larmor_step)


            SimpleDecoupling(SAMPLE+'_RepT_XY'+str(XY_scheme)+'_N_'+str(N)+'_part'+str(1+nr_of_runs),
                                    N=N,sweep=sweep,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, debug=debug,larmor_offset = larmor_offset)

    return Continue_bool
    ### optimize position for the following run.


if __name__ == '__main__':
    n=0
    Total_time = 0.
    debug = False
    Cont = True
    Run_Msmt = True
    n = 1
    qt.msleep(2)
    qt.instruments['purification_optimizer'].start_babysit()
    if n==1 and Cont:
        N = qt.decoupling_parameter_list[0] ### number of pulses
        pts = qt.decoupling_parameter_list[1] ### number of points per loading of the AWG
        larmor_freq = 1/qt.exp_params['samples'][qt.exp_params['samples']['current']]['C2_freq_0']#1/qt.exp_params['samples']['Pippin']['C1_freq_0']
        larmor_max = qt.decoupling_parameter_list[2] ### the order of the last revival
        larmor_min = qt.decoupling_parameter_list[3]
        larmor_step =  qt.decoupling_parameter_list[4]
        reps =  qt.decoupling_parameter_list[5]
        tau_larmor_offset =  qt.decoupling_parameter_list[6]

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*larmor_freq*larmor_min,2*Number_of_pulses*larmor_freq*larmor_max,nr_of_runs)) /3600.
        
        print Total_time
        #### need to start and stop the babysitter here.
        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,
                larmor_step=larmor_step,
                reps=reps,sweep = 'N',
                debug=debug,
                larmor_offset = tau_larmor_offset)
    qt.instruments['purification_optimizer'].stop_babysit()

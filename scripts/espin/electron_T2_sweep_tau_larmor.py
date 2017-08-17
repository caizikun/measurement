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
        return True

def SimpleDecoupling(name,N=4,end=100e-3,nr_list=[1], XY_scheme=8, reps=500,debug=False,larmor_offset = 0):

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


    
    Number_of_pulses = N

    tau_list =np.array([round(x*tau_larmor*0.25e9) / (0.25e9) for x in nr_list]) + larmor_offset
    m.params['tau_larmor_offset'] = larmor_offset

    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e3
    print m.params['sweep_pts']
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

def SimpleDecoupling_Single_Block(name,N=4,end=100e-3,nr_list=[1], XY_scheme=8, reps=500,debug=False,larmor_offset = 0):

    m = DD.SimpleDecoupling_Single_Block(name)
    funcs.prepare(m)

    # Details for multiple C13 Adwin script 
    m.params['use_shutter'] = shutter

    m.params['reps_per_ROsequence'] = reps #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'
    print 'XY_scheme', XY_scheme
    m.params['Number of pulses in XY scheme'] = XY_scheme
    m.params['DD_in_eigenstate'] = False
    ### Calculate tau larmor
    tau_larmor = np.round(1/m.params['C1_freq_0'],9)

    Number_of_pulses = N
    tau_list = nr_list*tau_larmor + larmor_offset
    m.params['tau_larmor_offset'] = larmor_offset

    print nr_list
    print tau_list
    print 2*tau_larmor
    m.params['pts']              = len(tau_list)
    m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
    m.params['tau_list']         = tau_list
    m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e3
    print m.params['sweep_pts'] 
    m.params['sweep_name']       = 'total evolution time (ms)'

    m.autoconfig()
    funcs.finish(m, upload =True, debug=debug)

def optimize():
    GreenAOM.set_power(7e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['z','x','y'], int_time = 120)
    stools.turn_off_all_lasers()


def take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=2,Single_Block=False,XY_scheme=8, reps=500, optimize=True, larmor_offset=0 ,debug=False):
    ## loop function for data acquisition.

    Continue_bool = True 

    larmor_steps = pts*larmor_step ### how many steps in in tau_larmor are taken
    nr_of_runs = int(np.floor((larmor_max-larmor_min)/larmor_steps))
    print 'nrofruns', nr_of_runs
    if qstop(sleep=3):
            Continue_bool = False
    else:
        for n in range(nr_of_runs):
            if qstop(sleep=3):
                Continue_bool = False
                break
            if optimize and not debug:
                optimize()

            print 'n', n
            nr_list = np.arange(larmor_min+n*larmor_steps,larmor_min+(n+1)*larmor_steps,larmor_step)
            print 'nr_list', nr_list
            if Single_Block:
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_XY'+str(XY_scheme)+'_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(n+1),
                                                    N=N,
                                                    nr_list = nr_list, larmor_offset = larmor_offset,
                                                    XY_scheme=XY_scheme, 
                                                    reps=reps,debug=debug)
            else:
                SimpleDecoupling(SAMPLE+'_RepT_XY'+str(XY_scheme)+'_N_'+str(N)+'_part'+str(n+1),
                                        N=N,nr_list = nr_list,larmor_offset = larmor_offset,
                                        reps=reps, XY_scheme=XY_scheme, debug=debug)

    ### get the remaining larmor revivals in.
    if Continue_bool:
        nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,larmor_step)

        if optimize and not debug:
            optimize()

        print 'nr_list', nr_list
        if Single_Block:
            SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_XY'+str(XY_scheme)+'_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(1+nr_of_runs),
                        N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug,larmor_offset = larmor_offset)

        else:
            SimpleDecoupling(SAMPLE+'_RepT_XY'+str(XY_scheme)+'_N_'+str(N)+'_part'+str(1+nr_of_runs),
                                    N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, debug=debug,larmor_offset = larmor_offset)

    return Continue_bool
    ### optimize position for the following run.


if __name__ == '__main__':
    n=0
    Total_time = 0.
    debug = False
    Cont = True
    Run_Msmt = True
    optimize = False
    n = 1


    DD_parameters_dict =     {
        '1'      : [1,480*8,400,2,8,1000], 
        '4'      : [4,480*4,250,2,8,1000],
        '8'      : [8,480*4,200,2,4,1000],
        '16'     : [16,480*2,150,2,4,1000],
        '32'     : [32,480,120,2,4,1000],
        '64'     : [64,240,120,2,4,1000],
        '128'     : [128,120,120,2,4,1000],
        '256'     : [256,400,100,2,2,1000],
        '512'     : [512,400,90,2,2,1000],
        '1024'     : [1024,400,80,2,2,1000],
    }




    if n==1 and Cont:
        n_pulses = '128'
        N = DD_parameters_dict[n_pulses][0] ### number of pulses
        pts =DD_parameters_dict[n_pulses][1] ### number of points per loading of the AWG
        larmor_freq = 1/qt.exp_params['samples']['Pippin']['C1_freq_0']
        larmor_max = DD_parameters_dict[n_pulses][2] ### the order of the last revival
        larmor_min = DD_parameters_dict[n_pulses][3]
        larmor_step = DD_parameters_dict[n_pulses][4]
        reps = DD_parameters_dict[n_pulses][5]
        tau_larmor_offset = 0e-9 #### this could be modified in a master script scenario

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*larmor_freq*larmor_min,2*Number_of_pulses*larmor_freq*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,
                larmor_step=larmor_step,
                optimize=optimize,
                XY_scheme=8,
                reps=reps,
                debug=debug,
                larmor_offset = tau_larmor_offset)


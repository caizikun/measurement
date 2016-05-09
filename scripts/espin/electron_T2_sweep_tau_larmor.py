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

def SimpleDecoupling(name, sweep = 'N',N=4,end=100e-3,nr_list=[1], shutter=0, XY_scheme=8, reps=500,debug=False):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['use_shutter'] = shutter
    m.params['reps_per_ROsequence'] = reps #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'

    tau_larmor = 1/m.params['C4_freq_0']
    if N==1:
        m.params['Final_Pulse'] ='x'
    else:
        m.params['Final_Pulse'] ='-x'
    ### Calculate tau larmor
    # f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    # tau_larmor = 1/f_larmor#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6
    

    # tau_larmor = 2.316e-6
    #tau_larmor = 2.524e-6
    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'tau':

        
        
        ### commented out for loop functionalities
        # pts = 20
        # start   = 0e-3 + tau_larmor*(2*Number_of_pulses) 
        # end     = 60e-3 
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        
        Number_of_pulses = N
        print nr_list*tau_larmor
        tau_list =np.array([round(x*tau_larmor*0.25e9) / (0.25e9) for x in nr_list])

        #to check collapses
        # tau_list = tau_list-0.25*tau_larmor

        print nr_list
        print tau_list
        print 2*tau_larmor

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
        else:
            raise Exception('XY Scheme not reckognized')
        #m.params['Decoupling_sequence_scheme']='single_block'


        m.autoconfig()
        funcs.finish(m, upload =True, debug=debug)

def SimpleDecoupling_Single_Block(name, sweep = 'N',N=4,end=100e-3,nr_list=[1], shutter=0, XY_scheme=8, reps=500,debug=False):

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
    # f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    # tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor
    tau_larmor = 1/m.params['C1_freq_0']#2.316e-6
    #tau_larmor = 2.524e-6

    print 'i was here'

    if sweep == 'tau':


        Number_of_pulses = N
        tau_list = nr_list*tau_larmor 

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


def take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=2,Single_Block=False,shutter=False,XY_scheme=8, reps=500, optimize=True,debug=False):
    ## loop function for data acquisition.
    # GreenAOM.set_power(20e-6)
    # counters.set_is_running(1)
    # optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
    # stools.turn_off_all_lasers()

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
                GreenAOM.set_power(7e-6)
                counters.set_is_running(1)
                optimiz0r.optimize(dims = ['x','y','z'], int_time = 120)
                stools.turn_off_all_lasers()

            print 'n', n
            nr_list = np.arange(larmor_min+n*larmor_steps,larmor_min+(n+1)*larmor_steps,larmor_step)
            print 'nr_list', nr_list
            if Single_Block:
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)
            else:
                SimpleDecoupling(SAMPLE+'_RepT_ShutterNO_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug)

    ### get the remaining larmor revivals in.
    if Continue_bool:
        nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,larmor_step)

        if optimize and not debug:
            GreenAOM.set_power(7e-6)
            counters.set_is_running(1)
            optimiz0r.optimize(dims = ['z','x','y'], int_time = 120)
            stools.turn_off_all_lasers()

        print 'nr_list', nr_list
        if Single_Block:
            SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(1+nr_of_runs),
                sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)

        else:
            SimpleDecoupling(SAMPLE+'_RepT_ShutterNO_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug)

    return Continue_bool
    ### optimize position for the following run.


if __name__ == '__main__':
    n=0
    Total_time = 0.
    debug = False
    Cont = True
    Run_Msmt = True
    optimize = True
    n = 1
    if n==1 and Cont:
        N = 64 ### number of pulses
        pts = 50 ### number of points per loading of the AWG
        larmor_freq = 2.26e-6
        larmor_max = 120 ### the order of the last revival
        larmor_min = 4
        larmor_step = 8
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*larmor_freq*larmor_min,2*Number_of_pulses*larmor_freq*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,
                larmor_step=larmor_step,
                optimize=optimize,
                Single_Block=False,
                shutter=False,
                XY_scheme=8,
                reps=reps,
                debug=debug)


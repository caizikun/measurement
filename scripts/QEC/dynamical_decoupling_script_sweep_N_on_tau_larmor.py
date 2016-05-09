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

    
    if N==1:
        m.params['Final_Pulse'] ='x'
    else:
        m.params['Final_Pulse'] ='-x'
    ### Calculate tau larmor
    #f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    #tau_larmor = 1/f_larmor#rounds to ns
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
    #f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    #tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor
    tau_larmor = 2.316e-6
    #tau_larmor = 2.524e-6



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


def take_DD_Data(larmor_nr,Nmin,Nmax,Nstep,Single_Block=False,shutter=False,XY_scheme=8, reps=500, optimize=True,debug=False):
    ## loop function for data acquisition.
    # GreenAOM.set_power(20e-6)
    # counters.set_is_running(1)
    # optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
    # stools.turn_off_all_lt2_lasers()

    Continue_bool = True 

    nr_list = np.array([larmor_nr])
    print 'nrofruns', nr_of_runs
    
    for n, N in enumerate(range(Nmin,Nmax+Nstep,Nstep)):
        if qstop(sleep=3):
            Continue_bool = False
            break
        if optimize and not debug:
            GreenAOM.set_power(7e-6)
            counters.set_is_running(1)
            optimiz0r.optimize(dims = ['x','y','z'], int_time = 120)
            #stools.turn_off_all_lt2_lasers()

        SimpleDecoupling(SAMPLE+'_RepT'+str(XY_scheme)+'sweep_N_on_tau_L'+ str(larmor_nr) + '_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug)

    ### get the remaining larmor revivals in.

    return Continue_bool
    ### optimize position for the following run.


if __name__ == '__main__':
    n=1
    Total_time = 0.
    debug = False
    Cont = True
    Run_Msmt = True
    optimize = False

    
  
    if n==1 and Cont:
        Nmin = 2
        Nmax = 100
        Nstep = 10
        larmor_nr = 5
        reps = 800
        tau_larmor = 1/447968.42
        pts = 10
        #Number_of_pulses = 5
        nr_of_runs = int(np.floor((Nmax-Nmin)/float(Nstep)))
        #Total_time += reps*sum(np.linspace(2*Number_of_pulses*tau_larmor*larmor_min,2*Number_of_pulses*tau_larmor*larmor_max,nr_of_runs)) /3600.

        #print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_nr,Nmin,Nmax,Nstep,pts,optimize=optimize,XY_scheme=8,reps=reps,debug=debug)

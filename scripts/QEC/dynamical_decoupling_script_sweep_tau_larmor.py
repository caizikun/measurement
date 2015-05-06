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

def SimpleDecoupling(name, sweep = 'N',N=4,end=100e-3,nr_list=[1]):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'

    ### Calculate tau larmor
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'N':
        Number_of_pulses=[50,500,3400]
        #Number_of_pulses = linspace(2,3003,500).astype(int)

        pts = len(Number_of_pulses)
        m.params['pts'] = pts
        tau_list = np.ones(pts)*tau_larmor
        m.params['tau_list'] = tau_list
        m.params['Number_of_pulses'] = Number_of_pulses
        m.params['sweep_pts'] = [x*tau_larmor*2e3 for x in Number_of_pulses]
        m.params['sweep_name'] = 'decoupling time (ms)'
        m.params['Decoupling_sequence_scheme']='repeating_T_elt'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

    if sweep == 'tau':

        
        
        ### commented out for loop functionalities
        # pts = 20
        # start   = 0e-3 + tau_larmor*(2*Number_of_pulses) 
        # end     = 60e-3 
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        
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
        m.params['Decoupling_sequence_scheme']='repeating_T_elt'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=False)

def SimpleDecoupling_Single_Block(name, sweep = 'N',N=4,end=100e-3,nr_list=[1], shutter=0, XY_scheme=8, reps=500):

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
    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)#rounds to ns
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor


    # if sweep == 'N':
    #     Number_of_pulses=[50,500,3400]
    #     #Number_of_pulses = linspace(2,3003,500).astype(int)

    #     pts = len(Number_of_pulses)
    #     m.params['pts'] = pts
    #     tau_list = np.ones(pts)*tau_larmor
    #     m.params['tau_list'] = tau_list
    #     m.params['Number_of_pulses'] = Number_of_pulses
    #     m.params['sweep_pts'] = [x*tau_larmor*2e3 for x in Number_of_pulses]
    #     m.params['sweep_name'] = 'decoupling time (ms)'
    #     m.params['Decoupling_sequence_scheme']='repeating_T_elt'

    #     m.autoconfig()
    #     funcs.finish(m, upload =True, debug=False)

    if sweep == 'tau':

        
        
        ### commented out for loop functionalities
        # pts = 20
        # start   = 0e-3 + tau_larmor*(2*Number_of_pulses) 
        # end     = 60e-3 
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        
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
        funcs.finish(m, upload =True, debug=False)


def take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=False,shutter=False,XY_scheme=8, reps=500):
    ## loop function for data acquisition.
    # GreenAOM.set_power(20e-6)
    # counters.set_is_running(1)
    # optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
    # stools.turn_off_all_lt2_lasers()

    Continue_bool = True 

    larmor_steps = pts*2. ### how many steps in in tau_larmor are taken
    nr_of_runs = int(np.floor((larmor_max-larmor_min)/larmor_steps))

    if qstop(sleep=4):
            Continue_bool = False
    else:
        for n in range(nr_of_runs):
            if qstop(sleep=4):
                Continue_bool = False
                break

            GreenAOM.set_power(20e-6)
            counters.set_is_running(1)
            optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
            stools.turn_off_all_lt2_lasers()

            print n
            nr_list = np.arange(larmor_min+n*larmor_steps,larmor_min-1+(n+1)*larmor_steps,2)
            print nr_list
            if Single_Block:
                if shutter:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterYES_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, shutter=1, XY_scheme=XY_scheme, reps=reps)
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                else:
                    SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps)
            else:
                SimpleDecoupling(SAMPLE+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list)
        
    ### get the remaining larmor revivals in.
    if Continue_bool:
        nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,2)
        if Single_Block:
            if shutter:
                adwin.start_set_dio(dio_no=4,dio_val=0)
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterYES_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),
                    sweep='tau',N=N,nr_list = nr_list, shutter=1, XY_scheme=XY_scheme, reps=reps)
                adwin.start_set_dio(dio_no=4,dio_val=0)
            else:
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),
                    sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps)

        else:
            SimpleDecoupling(SAMPLE+'sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),
                sweep='tau',N=N,nr_list = nr_list)
    return Continue_bool
    ### optimize position for the following run.


if __name__ == '__main__':
    n=0
    #######
    # Test msmt
    #######

    # N = 1024
    # pts = 2
    # larmor_max = 3
    # larmor_min = 3

    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True)
    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True)
    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=False)

    # n=0
    # '''
    # Difference is 4515 between two pulses
    # Between start and first 2256
    # 2258
    # '''
    
    #######
    # 128 pi - pulses
    # estimated T_coh = 25.4 ms @ T_Hahn approximately 1 ms
    #######

    ### need to exclude the first larmor revival, timing is too short when using the MW switch.
    ### measurement loop for several larmor revivals
    if n==1:
        N = 128
        pts = 20
        larmor_max = 145
        larmor_min = 3

        take_DD_Data(larmor_min,larmor_max,N,pts)


    ##############################
    ##############################

    #######
    # 256 pi - pulses
    # estimated T_coh = 40 ms @ T_Hahn approximately 1 ms
    # sweep until 100 ms overall evolution time --> 100/(2.315*e-3*2*256) = 84....
    # --> sweep until tau = 85*tau_larmor.
    #######

    if n==1:
        N = 256 ### number of pulses
        pts = 12 ### number of points per loading of the AWG
        larmor_max = 111 ### the order of the last revival
        larmor_min = 3

        '''Start at larmor_min = 1'''

        
        take_DD_Data(larmor_min,larmor_max,N,pts)
    
    ##############################
    ##############################

    #######
    # 512 pi - pulses
    # estimated T_coh = 64 ms @ T_Hahn approximately 1 ms
    # sweep until 130 ms overall evolution time --> 140/(2.315*e-3*2*512) = 59....
    # --> sweep until tau = 59*tau_larmor.
    #######

    # ### measurement loop for several larmor revivals
    if n == 1:
        N = 512 ### number of pulses
        pts = 7 ### number of points per loading of the AWG
        larmor_max = 91 ### the order of the last revival
        larmor_min = 3

        
        take_DD_Data(larmor_min,larmor_max,N,pts)

    ##############################
    ##############################
  
    #######
    # 1024 pi - pulses
    # estimated T_coh = 101 ms @ T_Hahn approximately 1 ms
    # sweep until 200 ms overall evolution time --> 200/(2.315*e-3*2*1024) = 42...
    # --> sweep until tau = 61*tau_larmor.
    #######

    # ### measurement loop for several larmor revivals
    if n==1:
        N = 1024 ### number of pulses
        pts = 3 ### number of points per loading of the AWG
        larmor_max = 71 ### the order of the last revival
        larmor_min = 3

        take_DD_Data(larmor_min,larmor_max,N,pts)
     

    ##############################
    ##############################
    
    #######
    # 2048 pi - pulses
    # estimated T_coh = 161 ms @ T_Hahn approximately 1 ms
    # sweep until 300 ms overall evolution time --> 300/(2.315*e-3*2*2048) = 31.6
    # --> sweep until tau = 61*tau_larmor.
    #######

    ### measurement loop for several larmor revivals
    if n==1:
        N = 2048 ### snumber of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 61 ### the order of the last revival
        larmor_min = 3

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts)
    

    #######
    # 4096 pi - pulses
    # estimated T_coh = 256 ms @ T_Hahn approximately 1 ms
    # sweep until 500 ms overall evolution time --> 500/(2.315*e-3*2*4096) = 27
    # --> sweep until tau = 61*tau_larmor.
    #######
    if n==1 and Cont:
        N = 4096 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 51
        larmor_min = 31

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)



    # if n==1:
    # ### measurement loop for several larmor revivals
    #     N = 32768 ### number of pulses
    #     pts = 1 ### number of points per loading of the AWG
    #     # larmor_max = 49 ### the order of the last revival
    #     larmor_max = 1
    #     larmor_min = 1

    #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)

    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)

    #     N = 65536
    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)
    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)

    #     # N = 16384
    #     # if Cont:
    #     #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)
    #     # if Cont:
    #     #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)
    n=1
   

    Total_time = 0.
    Cont = True

    #######
    # 65536 pi - pulses
    # estimated T_coh = 1626 ms @ T_Hahn approximately 1 ms
    # sweep until 3300 ms overall evolution time --> 3300/(2.315*e-3*2*65536) = 10.9
    # --> sweep until tau = 17*tau_larmor.
    #######
    if n==1 and Cont:
        N = 65536 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 4
        larmor_min = 2
        reps = 1000

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/2.))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)


    #######
    # 32768 pi - pulses
    # estimated T_coh = 1024 ms @ T_Hahn approximately 1 ms
    # sweep until 2100 ms overall evolution time --> 2100/(2.315*e-3*2*32768) = 13.8
    # --> sweep until tau = 21*tau_larmor.
    #######
    if n==1 and Cont:
        N = 32768 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 21
        larmor_min = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/2.))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    #######
    # 16384 pi - pulses
    # estimated T_coh = 645 ms @ T_Hahn approximately 1 ms
    # sweep until 1200 ms overall evolution time --> 1200/(2.315*e-3*2*16384) = 15.8
    # --> sweep until tau = 25*tau_larmor.
    #######
    if n==1 and Cont:
        N = 16384 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 27
        larmor_min = 1
        reps = 650

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/2.))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)
    
    #######
    # 8192 pi - pulses
    # estimated T_coh = 406 ms @ T_Hahn approximately 1 ms
    # sweep until 800 ms overall evolution time --> 800/(2.315*e-3*2*8192) = 21.1
    # --> sweep until tau = 41*tau_larmor.
    #######
    if n==1 and Cont:
        N = 8192 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 31
        larmor_min = 1
        reps = 500

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/2.))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)


    #######
    # 4096 pi - pulses
    # estimated T_coh = 256 ms @ T_Hahn approximately 1 ms
    # sweep until 500 ms overall evolution time --> 500/(2.315*e-3*2*4096) = 27
    # --> sweep until tau = 61*tau_larmor.
    #######
    if n==1 and Cont:
        N = 4096 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 41
        larmor_min = 1
        reps = 400

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/2.))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    
    print Total_time
    
    
    # execfile(r'D:\measuring\measurement\scripts\QEC\carbon_calibration_routine_v2.py')


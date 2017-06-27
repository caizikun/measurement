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
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD
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
    m.params['DD_in_eigenstate'] = False # overwrites the use of pi/2 pulses.
    
    if N==1:
        m.params['Final_Pulse'] = 'x'
    else:
        m.params['Final_Pulse'] = '-x'
    ### Calculate tau larmor
    tau_larmor = round(1/442812.73,9)

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

    tau_larmor = round(1/442812.73,9)
    print 'tau_larmor = %s' %tau_larmor



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
                if shutter:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterYES_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, shutter=1, XY_scheme=XY_scheme, reps=reps,debug=debug)
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                else:
                    SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)
            else:
                if shutter:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    SimpleDecoupling(SAMPLE+'_RepT_ShutterYES_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=1, debug=debug)
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                else:
                    SimpleDecoupling(SAMPLE+'_RepT_ShutterNO_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug)

    ### get the remaining larmor revivals in.
    if Continue_bool:
        nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,larmor_step)

        if optimize and not debug:
            GreenAOM.set_power(7e-6)
            counters.set_is_running(1)
            optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
            stools.turn_off_all_lasers()

        print 'nr_list', nr_list
        if Single_Block:
            if shutter:
                adwin.start_set_dio(dio_no=4,dio_val=0)
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterYES_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(1+nr_of_runs),
                    sweep='tau',N=N,nr_list = nr_list, shutter=1, XY_scheme=XY_scheme, reps=reps,debug=debug)
                adwin.start_set_dio(dio_no=4,dio_val=0)
            else:
                SimpleDecoupling_Single_Block(SAMPLE+'_Single_Block_ShutterNO_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(1+nr_of_runs),
                    sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)

        else:
            if shutter:
                adwin.start_set_dio(dio_no=4,dio_val=0)
                SimpleDecoupling(SAMPLE+'_RepT_ShutterYES_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=1, debug=debug)
                adwin.start_set_dio(dio_no=4,dio_val=0)
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
    optimize = False

    if n==1 and Cont:
        N = 1024 ### number of pulses
        pts = 2 ### number of points per loading of the AWG
        larmor_max = 91 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    n=0
    if n==1 and Cont:
        N = 64
        pts = 30
        larmor_max = 200
        larmor_min = 2
        larmor_step = 3
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    if n==1 and Cont:
        N = 32
        pts = 40
        larmor_max = 222
        larmor_min = 2
        larmor_step = 5
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    if n==1 and Cont:
        N = 16
        pts = 60
        larmor_max = 270
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    if n==1 and Cont:
        N = 8
        pts = 70
        larmor_max = 380
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    if n==1 and Cont:
        N = 4
        pts = 70
        larmor_max = 352
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)
    
    n=1     
    if n==1 and Cont:
        N = 1
        pts = 70
        larmor_max = 350
        larmor_min = 2
        larmor_step = 10
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)
         

    n=0


    if n==1 and Cont:
        debug = False
        N = 1
        pts = 60
        larmor_max = 350
        larmor_min = 2
        larmor_step = 10
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)
      
    n=0      
    ######
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
    ###
    # 128 pi - pulses
    # estimated T_coh = 25.4 ms @ T_Hahn approximately 1 ms
    #######




    n=0
    ### need to exclude the first larmor revival, timing is too short when using the MW switch.
    ### measurement loop for several larmor revivals
    if n==1 and Cont:
        N = 128
        pts = 20
        larmor_max = 151
        larmor_min = 2
        larmor_step = 2
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    n=0
    ##############################
    ##############################

    #######
    # 256 pi - pulses
    # estimated T_coh = 40 ms @ T_Hahn approximately 1 ms
    # sweep until 100 ms overall evolution time --> 100/(2.315*e-3*2*256) = 84....
    # --> sweep until tau = 85*tau_larmor.
    #######

    if n==1 and Cont:
        N = 256 ### number of pulses
        pts = 10 ### number of points per loading of the AWG
        larmor_max = 131 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        '''Start at larmor_min = 1'''
        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    
    ##############################
    ##############################

    #######
    # 512 pi - pulses
    # estimated T_coh = 64 ms @ T_Hahn approximately 1 ms
    # sweep until 130 ms overall evolution time --> 140/(2.315*e-3*2*512) = 59....
    # --> sweep until tau = 59*tau_larmor.
    #######
 
    # ### measurement loop for several larmor revivals


    if n == 1 and Cont:
        N = 512 ### number of pulses
        pts = 5 ### number of points per loading of the AWG
        larmor_max = 115 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    ##############################
    ##############################
  
    #######
    # 1024 pi - pulses
    # estimated T_coh = 101 ms @ T_Hahn approximately 1 ms
    # sweep until 200 ms overall evolution time --> 200/(2.315*e-3*2*1024) = 42...
    # --> sweep until tau = 61*tau_larmor.
    #######

    # ### measurement loop for several larmor revivals
    
    #execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')


    ##############################
    ##############################
    
    #######
    # 2048 pi - pulses
    # estimated T_coh = 161 ms @ T_Hahn approximately 1 ms
    # sweep until 300 ms overall evolution time --> 300/(2.315*e-3*2*2048) = 31.6
    # --> sweep until tau = 61*tau_larmor.
    #######

   
    
    
    n = 0
    ### measurement loop for several larmor revivals
    if n==1 and Cont:
        N = 2048 ### snumber of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 66 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += 2.*reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        # Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=False,XY_scheme=8,reps=reps)
        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=8,reps=reps,debug=debug)
        # Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps)
    n = 0
    #execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')
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

    '''
    Stel je hebt 10 punten
    stopts punt 3
    start punt 7
    delta = 4
    stopt punt 7
    9-7 = 2
    start punt 2


    '''


    '''
    Rep Tr
    between pi2 and end 1472
    number of tau = 4
    between end and first pi 1390

    between pi and end 2390
    number of tau = 9
    between start and second pi (Y)  2390
    total = 13780

    Single Block
    between pi2 and end 6864

    between pi and pi 13781

    between pi and end 6890
    between start and pi 6890
    = 13780


    '''
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

    #######
    # 65536 pi - pulses
    # estimated T_coh = 1626 ms @ T_Hahn approximately 1 ms
    # sweep until 3300 ms overall evolution time --> 3300/(2.315*e-3*2*65536) = 10.9
    # --> sweep until tau = 17*tau_larmor.
    #######
    if n==1 and Cont:
        N = 65536 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 3
        larmor_min = 3
        larmor_step = 1
        reps = 900

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=False,XY_scheme=16,reps=reps)

   


    #######
    # 32768 pi - pulses
    # estimated T_coh = 1024 ms @ T_Hahn approximately 1 ms
    # sweep until 2100 ms overall evolution time --> 2100/(2.315*e-3*2*32768) = 13.8
    # --> sweep until tau = 21*tau_larmor.
    #######

    if n==1 and Cont:
        N = 32768 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 15
        larmor_min = 1
        larmor_step = 1
        reps = 700

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    #######
    # 16384 pi - pulses
    # estimated T_coh = 645 ms @ T_Hahn approximately 1 ms
    # sweep until 1200 ms overall evolution time --> 1200/(2.315*e-3*2*16384) = 15.8
    # --> sweep until tau = 25*tau_larmor.
    #######
    if n==1 and Cont:
        N = 16384 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 17
        larmor_min = 1
        larmor_step = 1
        reps = 600

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    #######
    # 8192 pi - pulses
    # estimated T_coh = 406 ms @ T_Hahn approximately 1 ms
    # sweep until 800 ms overall evolution time --> 800/(2.315*e-3*2*8192) = 21.1
    # --> sweep until tau = 41*tau_larmor.
    #######
    if n==1 and Cont:
        N = 8192 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 23
        larmor_min = 1
        larmor_step = 1
        reps = 450

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)


    #######
    # 4096 pi - pulses
    # estimated T_coh = 256 ms @ T_Hahn approximately 1 ms
    # sweep until 500 ms overall evolution time --> 500/(2.315*e-3*2*4096) = 27
    # --> sweep until tau = 61*tau_larmor.
    #######
    if n==1 and Cont:
        N = 4096 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 29
        larmor_min = 1
        larmor_step = 1
        reps = 400

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    # if Run_Msmt and Cont and n==1:
    #     execfile(r'D:\measuring\measurement\scripts\QEC\carbon_calibration_routine_v2.py')


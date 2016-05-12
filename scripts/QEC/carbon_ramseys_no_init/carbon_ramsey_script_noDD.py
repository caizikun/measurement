"""
Script for a carbon ramsey sequence, without electron DD during the waiting time.
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs
reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def interrupt_script():
    print 'press q now to exit measurement script'
    qt.msleep(5)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        sys.exit()

def optimize_NV():
    qt.msleep(2)
    AWG.clear_visa()
    stools.turn_off_all_lasers()
    qt.msleep(1)
    GreenAOM.set_power(50e-6)
    optimiz0r.optimize(dims=['x','y','z','x','y'], cycles = 1)

def Carbon_Ramsey(name, t_start = None, t_end = None, pts = None, mbi = False, tau = None, N=None):

    if t_start != None and t_end != None:
        name = name + '_t=[%s-%s]' % (t_start, t_end)
        m = DD.NuclearRamsey_no_elDD(name)
    else:
        m = DD.NuclearRamsey_no_elDD(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse']       = 'x'
    m.params['Final_Pulse']         = '-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'
    
    m.params['addressed_carbon'] = 4
    m.name += '_carbon%s' % m.params['addressed_carbon']
    ### Sweep parameter ###
    if t_start != None and t_end != None and pts != None:
        m.params['free_evolution_times'] = np.linspace(t_start*1e3,t_end*1e3,pts).astype(int)*1e-9
    else:
        # m.params['free_evolution_times'] = np.linspace(554,650,21).astype(int)*1e-6
        m.params['free_evolution_times'] = np.concatenate( (np.array([4]), np.linspace(700, 8400, 12))) * 1e-6
        m.name = name + '_t=[%s-%s]' % (int(np.amin(m.params['free_evolution_times'])*1e6), int(np.amax(m.params['free_evolution_times'])*1e6) )    
        print m.name

    print 'free evolution times: %s' % (m.params['free_evolution_times'] * 1e6 )
    m.params['pts']              = len(m.params['free_evolution_times'])
    m.params['sweep_pts']        = m.params['free_evolution_times'] * 1e6
    m.params['sweep_name']       = 'Free evolution time (us)'

    if mbi == False:
        m.params['MBI_threshold'] = 0
        m.params['Ex_SP_amplitude'] = 0
        m.params['Ex_MBI_amplitude'] = 0
        m.params['SP_E_duration'] = 20 #2000
        
        m.params['repump_after_MBI_A_amplitude'] = [15e-9]
        m.params['repump_after_MBI_duration'] = [300] # 50

    # if N ==None: 
    #     m.params['C_Ren_N'] = m.params['C5_Ren_N'][0]  
    # else:
    #     m.params['C_Ren_N'] = N
    # if tau ==None: 
    #     m.params['C_Ren_tau'] = m.params['C5_Ren_tau'][0]
    # else: 
    #     m.params['C_Ren_tau'] = tau 

    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)
    print m.params['sweep_pts'] 

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE, t_start = 15, t_end = 75, pts = 46)
    # interrupt_script()
    # optimize_NV()
    # Carbon_Ramsey(SAMPLE, t_start = None, t_end = None, pts = None)
    # tau_start = np.arange(2854, 3855, 100)
    # for tau_start in tau_start:
    #     Carbon_Ramsey(SAMPLE, t_start = tau_start , t_end = tau_start + 96, pts = 21)
    #     interrupt_script()
    #     optimize_NV()


# if __name__ == '__main__':
#     tau_list = np.linspace(6.522e-6-20e-9,6.522e-6+20e-9,21)
#     for tau in tau_list:
#         print tau 
#         Carbon_Ramsey(SAMPLE+str(tau),tau, N=16)

#         print 'press q now to cleanly exit this measurement loop'
#         qt.msleep(5)
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
#             break


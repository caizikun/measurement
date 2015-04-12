"""
Script for a carbon Hahn echo sequence.
Initialization:
- Initializes in the 1 state using Swap
- Can set the electron state by setting the MBI succes condition

Hahn echo
- Applies two pi / 2 pulses along x-axis to apply one pi pulse

Measurement
- Measures Carbon state along X,Y,Z axis. Should allign along Z.
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Single_C_XY4(name, 
        carbon_nr             = 1,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = True,
        pulses                = 4,
        el_after_init = 1,
        C13_init_method       = 'MBI'):

    m = DD.NuclearXY4(name)
    funcs.prepare(m)

    '''Set parameters'''

    m.params['el_after_init'] = el_after_init 
    m.params['Decoupling_pulses']=pulses
    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 400
    m.params['C13_MBI_RO_state'] = 0 
    m.params['C13_MBI_threshold_list'] = [0] #Zero as we are detecting ms=-1 with laser resonance on other transition
    m.params['C13_MBI_RO_duration'] = 100 #Chaning readout laser duration to ensure m_s=-1 

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    # m.params['use_shutter'] = 1
    ### overwritten from msmnt params
           
     # Free evolution time in the order of

    #############################
    ### Option 1; Sweep phase ###
    #############################

    if False:
        m.params['C_RO_phase'] = ['X','Y','Z']
        m.params['pts'] = len(m.params['C_RO_phase'])
        m.params['free_evolution_time'] = [10e-3]*len(m.params['C_RO_phase'])
        m.params['sweep_name'] = 'phase'
        m.params['sweep_pts']  = m.params['C_RO_phase']
    
    ######################################
    ### Option 2; Sweep evolution time ###
    ######################################
    
    if True:
        if pulses == 4:
            m.params['free_evolution_time'] = np.linspace(1.5e-3,150e-3,8)
        else:
            m.params['free_evolution_time'] = np.linspace(1.5e-3,100e-3,4)
        m.params['pts'] = len(m.params['free_evolution_time'])
        m.params['C_RO_phase'] = ['X']*len(m.params['free_evolution_time'])
        m.params['sweep_name'] = 'Free evolution time (s)'
        m.params['sweep_pts']  = m.params['free_evolution_time']*2*m.params['Decoupling_pulses']

    
  
    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    carbon = 5
    pulses = 8
    el_RO = 'positive'
    Single_C_XY4(SAMPLE+'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses), carbon_nr = carbon, el_RO='positive',pulses = pulses)

    # GreenAOM.set_power(20e-6)
    # adwin.start_set_dio(dio_no=4,dio_val=0)
    # optimiz0r.optimize(dims=['x','y','z','x','y'])
    # adwin.start_set_dio(dio_no=4,dio_val=0)

    # pulses = 4
    # Single_C_XY4(SAMPLE+'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses), carbon_nr = carbon, el_RO='positive',pulses = pulses)

    # GreenAOM.set_power(20e-6)
    # adwin.start_set_dio(dio_no=4,dio_val=0)
    # optimiz0r.optimize(dims=['x','y','z','x','y'])
    # adwin.start_set_dio(dio_no=4,dio_val=0)

    # el_RO = 'negative'
    # Single_C_XY4(SAMPLE+'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses), carbon_nr = carbon, el_RO='positive',pulses = pulses)

    # GreenAOM.set_power(20e-6)
    # adwin.start_set_dio(dio_no=4,dio_val=0)
    # optimiz0r.optimize(dims=['x','y','z','x','y'])
    # adwin.start_set_dio(dio_no=4,dio_val=0)

    # pulses = 8
    # Single_C_XY4(SAMPLE+'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses), carbon_nr = carbon, el_RO='positive',pulses = pulses)
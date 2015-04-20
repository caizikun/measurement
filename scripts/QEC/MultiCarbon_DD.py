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
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Multi_C_DD(name,   
        carbon_init_list        = [1,2],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['MBI'], 
        carbon_init_thresholds  = 2*[1],   
        el_RO                   = 'positive',
        el_after_init           = 1,
        
        C13_DD_scheme           = 'auto',
        pulses                  = 4,
        free_evolution_time     = np.zeros((1)),
        single_Tomo_basis       = ['X','X']

        mode                    = 'Sweep evolution time'
        debug                   = False):

    m = DD.MultiNuclearDD(name)
    funcs.prepare(m)

    '''Set parameters'''

    m.params['C13_DD_Scheme'] = C13_DD_scheme
    m.params['el_after_init'] = el_after_init 
    m.params['Decoupling_pulses']=pulses

    m.params['reps_per_ROsequence'] = 350

    m.params['carbon_init_list']        = carbon_init_list
    m.params['init_method_list']        = carbon_init_methods    
    m.params['init_state_list']         = carbon_init_states 
    m.params['C13_MBI_threshold_list']  = carbon_init_thresholds
    m.params['Nr_C13_init']             = len(carbon_init_list)
    m.params['electron_readout_orientation'] = el_RO

    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    m.params['use_shutter'] = 1

    #############################
    ### Option 1; Sweep phase ###
    #############################

    if mode == 'Sweep phase':
        m.params['Tomography Bases'] = ([['X','I'],['I','X'],['X','X']])
        m.params['pts'] = len(m.params['Tomography Bases'])
        m.params['free_evolution_time'] = [0.001e-3]*m.params['pts']
        m.params['free_evolution_time_RO'] = [0.001e-3]*m.params['pts']
        m.params['sweep_name'] = 'Tomography bases'
        m.params['sweep_pts']  = []
        for BP in m.params['Tomography Bases']:
            if len(carbon_list) == 2:
                m.params['sweep_pts'].append(BP[0]+BP[1])
            elif len(carbon_list) == 3:
                m.params['sweep_pts'].append(BP[0]+BP[1]+BP[2])

    ######################################
    ### Option 2; Sweep evolution time ###
    ######################################

    elif mode == 'Sweep evolution time':
        m.params['free_evolution_time'] = free_evolution_time
        m.params['free_evolution_time_RO'] = free_evolution_time
        m.params['pts'] = len(m.params['free_evolution_time'])
        m.params['sweep_name'] = 'Free evolution time (s)'
        m.params['sweep_pts']  = m.params['free_evolution_time']*2*pulses 
        m.params['Tomography Bases'] = m.params['pts']*[single_Tomo_basis]

    ####################################################
    ### Option 3; Sweep assymetric RO evolution time ###
    ####################################################
  
    elif mode == 'Sweep RO evolution time':
        Diff_FET = np.linspace(-2e-6,2e-6,10)
        m.params['pts'] = len(Diff_FET)
        m.params['free_evolution_time'] = m.params['pts']*[20e-6]
        m.params['free_evolution_time_RO'] = Diff_FET+20e-6

        m.params['sweep_name'] = 'Delta Free Evolution time (ms)'
        m.params['sweep_pts']  =  Diff_FET*10e6
        m.params['Tomography Bases'] = m.params['pts']*[single_Tomo_basis]

    else:
        raise Exception('Mode not recognized')
    funcs.finish(m, upload =True, debug=debug)

def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    
    if RO_power != None: 
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None: 
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')
    
    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9#20e-9
    m.run()
    m.save('ms1')

    m.finish()

def qstop():
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

def Carbon_DD_mult_msmts(DD_scheme='XY4',carbons=[1],pulses_list=[4],el_ROs=['positive'],optimize=True, ssrocalib=True, 
    Max_FET_Dict = {'1': 1.3,'4': 2.25,'8': 3.0,'16': 5.,'32': 7.}, timepart_Dict ={'1': 1,'4': 2,'8': 4,'16': 8,'32': 8},
    debug=False, datapoints = 8, time_min= 20e-3):
    counter = 0
    for carbon in carbons:
        if qstop():
            break
        for pulses in pulses_list:
            if qstop():
                break
            FET = np.linspace(max(time_min/(2*pulses),1.5e-3),Max_FET_Dict[str(pulses)]/(2*pulses),datapoints)
            print FET
            indexer = datapoints/timepart_Dict[str(pulses)]
            for el_RO in el_ROs:
                if qstop():
                    break
                for timepart in range(timepart_Dict[str(pulses)]):
                    if qstop():
                        break
                    if ssrocalib and not debug:
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        ssrocalibration(SAMPLE)
                    if optimize and not debug:
                        GreenAOM.set_power(20e-6)
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
                    if ssrocalib and not debug:
                        adwin.start_set_dio(dio_no=4,dio_val=0)
                        ssrocalibration(SAMPLE)
                    counter +=1    
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    msmtstr = SAMPLE+'_'+ DD_scheme +'_C'+str(carbon) +'_RO' + el_RO + '_N' + str(pulses).zfill(2) + '_part' + str(timepart+1)
                    # Single_C_DD(msmtstr, carbon_nr = carbon, el_RO=el_RO,pulses = pulses, C13_DD_scheme=DD_scheme, debug=debug, free_evolution_time=FET[timepart*indexer:(timepart+1)*indexer])
                    print "Counter", counter
        

if __name__ == '__main__':

    carbon_init_list = [1,2]
    el_RO_list = ['positive','negative']
    pulses = 1
    single_Tomo_basis = [['X','X']


    msmtstring = 
    Multi_C_DD(carbon)
    

    
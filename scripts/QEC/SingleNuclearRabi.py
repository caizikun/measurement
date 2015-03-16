"""
Written by MAB
Script for a single Nuclear Rabi
Initialization:
- Initializes in the nuclear |0> state using SWAP

Rabi
- Sweep the pulse of an RF length

Readout
- Readout in Z basis

Copy from nitogen_rabipy in lt2_scripts/adwin_ssro/BSM
Copy from BSM.py in lt2_scripts/adwin_ssro/BSM

"""


import numpy as np
import qt 
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbifuncs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def CarbonRabiWithDirectRF(name, 
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = True,
        C13_init_method       = 'swap', 
        el_after_init         = '1',
        DoRabi                = False):

    m = DD.NuclearRabiWithDirectRF(name)
    funcs.prepare(m)


    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence']     = 1000
    m.params['C13_MBI_threshold_list']  = [0] 


    
    if DoRabi: 
        m.params['RF_pulse_durations'] = np.linspace(0e-6, 2e-3, 10)
        m.params['pts'] = len(m.params['RF_pulse_durations'])
        m.params['RF_pulse_frqs'] = np.ones(m.params['pts']) * m.params['C' + str(carbon_nr) + '_freq_' + el_after_init] + 30e3
        m.params['sweep_name'] = 'RF_pulse_length (us)'
        m.params['sweep_pts']  =  m.params['RF_pulse_durations'] / 1e-6 
    else: 
        # centerfreq = m.params['C' + str(carbon_nr) + '_freq_' + el_after_init]
        # FWHM = 100 #1/T2star = 1/10ms 
        m.params['RF_pulse_frqs'] = freqs
        m.params['pts'] = len(m.params['RF_pulse_frqs'])
        m.params['RF_pulse_durations'] = np.ones(m.params['pts']) * 6e-3
        m.params['sweep_name'] = 'RF_freq (kHz)'
        m.params['sweep_pts']  =  m.params['RF_pulse_frqs'] / 1e3        


    print  m.params['RF_pulse_frqs'][0]
   
    m.params['RF_pulse_amps'] = np.ones(m.params['pts']) * 0.1#0.04
    m.params['C_RO_phase'] = m.params['pts']*['Z']        


    

    m.params['C13_init_method'] = C13_init_method
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['el_after_init']                = el_after_init

    m.params['Nr_C13_init']       = 1 
    m.params['Nr_MBE']            = 0 
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':
    # CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C5_el0_positive', carbon_nr=5, el_RO= 'positive', el_after_init='0', DoRabi=True)
    
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C5_el1_positive', carbon_nr=5, el_RO= 'positive', el_after_init='1', DoRabi=True)

    print michiel

    carbon_nr = 5
    el_after_init = '1'
    centerfreq = qt.exp_params['samples']['111_1_sil18']['C'+ str(carbon_nr) + '_freq_'+ el_after_init]
    Freq = np.linspace(centerfreq-2.5e2,centerfreq+2.5e2,3)
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_1run', Freq, carbon_nr=carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=False)







# # centerfreq = 400e3
# # FWHM = 100
# # Freq = np.linspace(centerfreq-40*FWHM,centerfreq+40*FWHM,11)
# # Freq = np.unique(np.concatenate(Freq, np.linspace(centerfreq-40*FWHM,centerfreq+40*FWHM,11)))
# # CarbonRabiWithDirectRF(SAMPLE + 'NMR_C5_el1_positive', carbon_nr=5, el_RO= 'positive', el_after_init='1', DoRabi= False)
# #  #   CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C5_el1_negative', carbon_nr=5, el_RO= 'negative', el_after_init='1', DoRabi= False)
    carbon_nr = 5
    el_after_init = '1'
    centerfreq = qt.exp_params['samples']['111_1_sil18']['C'+ str(carbon_nr) + '_freq_'+ el_after_init]
    
    nr_per_round = 2
    nr_pts = 31
    Freq = np.linspace(centerfreq-2.5e2,centerfreq+2.5e2,nr_pts)
    length = nr_pts / nr_per_round - 1
    for i in range(length):

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_' +str(i)+'run', Freq[i*2:i*2+2], carbon_nr=carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=False)
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_'+str(length)+'run', Freq[nr_pts-np.mod(nr_pts,nr_per_round):nr_pts], carbon_nr=carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=False)


    print '\a', '\a', '\a'


    carbon_nr = 2
    el_after_init = '1'
    centerfreq = qt.exp_params['samples']['111_1_sil18']['C'+ str(carbon_nr) + '_freq_'+ el_after_init]
    
    nr_per_round = 2
    nr_pts = 31
    Freq = np.linspace(centerfreq-2.5e2,centerfreq+2.5e2,nr_pts)
    length = nr_pts / nr_per_round - 1
    for i in range(length):

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_' +str(i)+'run', Freq[i*2:i*2+2], carbon_nr=carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=False)
    CarbonRabiWithDirectRF(SAMPLE + 'Rabi_C'+str(carbon_nr)+'_el1_positive_'+str(length)+'run', Freq[nr_pts-np.mod(nr_pts,nr_per_round):nr_pts], carbon_nr=carbon_nr, el_RO= 'positive', el_after_init=el_after_init, DoRabi=False)


    print '\a', '\a', '\a', 
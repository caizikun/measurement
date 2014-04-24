"""
Script for a carbon ramsey sequence
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

def Carbon_Ramsey(name):

    m = DD.NuclearRamsey(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'
    m.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

    ### Sweep parmater
    m.params['free_evolution_time'] = np.array(range(15000,15500,10))*1e-9
    print m.params['free_evolution_time']
    m.params['pts']              = len(self.params['free_evolution_time'])
    m.params['sweep_pts']        =self.params['free_evolution_time']*1e6
    m.params['sweep_name']       = 'Free evolution time (us)'

    m.params['C_Ren_N'] = 16 # Currently arbitrary self.params['C1_Ren_N']
    m.params['C_Ren_tau'] = self.params['C1_Ren_tau']


    #############################
    #!NB: These should go into msmt params
    #############################
    m.params['min_dec_tau'] = 40e-9 + m.params['fast_pi_duration']
    m.params['max_dec_tau'] = 0.4e-6 #Based on simulation for fingerprint at low tau
    m.params['dec_pulse_multiple'] = 4 #lowest multiple of 4 pulses



    m.autoconfig()
    funcs.finish(m, upload =True, debug=False)

if __name__ == '__main__':
    Carbon_Ramsey(SAMPLE)



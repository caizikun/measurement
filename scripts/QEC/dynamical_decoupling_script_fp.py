"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
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

def SimpleDecoupling(name, sweep = 'tau2'):

    for kk in range(10):
        m = DD.SimpleDecoupling(name)
        funcs.prepare(m)

        '''set experimental parameters'''
        m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point

        m.params['Initial_Pulse'] ='x'
        m.params['Final_Pulse'] ='-x'

        Number_of_pulses = 32 #256
        pts = 51

        start    = 15.5e-6   + kk*0.5e-6
        end      = 15.5e-6   + kk*0.5e-6
        tau_list = np.linspace(start, end, pts)
        print tau_list

        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        = tau_list*1e6
        print m.params['sweep_pts']
        m.params['sweep_name']       = 'tau (us)'

        m.autoconfig()
        print 'run = ' + str(kk)
        funcs.finish(m, upload =True, debug=False)

        AWG.delete_all_waveforms_from_list()

if __name__ == '__main__':
    SimpleDecoupling('Fingerprint_' +SAMPLE+'_N32'+'')



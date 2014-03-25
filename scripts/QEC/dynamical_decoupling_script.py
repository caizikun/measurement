"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt
#import measurement.lib.config.adwins as adwins_cfg
#import measurement.lib.measurement2.measurement as m2 #Commented out because linter says it is unused

# import the msmt class
#from measurement.lib.measurement2.adwin_ssro import ssro
#from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
import measurement.lib.pulsar.DynamicalDecoupling as DD

reload(DD)

SAMPLE = qt.cfgman['samples']['current']
SAMPLE_CFG = qt.cfgman['protocols']['current']

def SimpleDecoupling(name):

    m = DD.SimpleDecoupling(name)

    m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['pulses'])


    '''set experimental parameters'''
        #Spin pumping and readout
    m.params['SP_duration'] = 250
    m.params['Ex_RO_amplitude'] = 8e-9 #10e-9
    m.params['A_SP_amplitude'] = 40e-9
    m.params['Ex_SP_amplitude'] = 0.
    m.params['repetitions'] = 2000

        #Set sequence wait time for AWG triggering (After AWG trigger? Tim)
    m.params['sequence_wait_time'] = 0

        #Plot parameters
    m.params['sweep_name'] = 'tau (us)'
    m.params['sweep_pts'] =np.linspace(2.975e-6,10.0*2.975e-6,10) # m.params['tau_list']*1e6  #np.linspace(1,10,10)#
    m.params['pts'] = 10#len(m.params['sweep_pts']) 
    m.autoconfig()

    #Decoupling specific parameters
    m.params['Number_of_pulses'] = 8
    m.params['tau_list'] = np.linspace(2.975e-6,10.0*2.975e-6,10) #Larmor period for B =314G
    m.params['Initial_Pulse'] ='pi/2'
    m.params['Final_Pulse'] ='pi/2'



    '''generate sequence'''
    m.generate_sequence(upload=True)


    #m.run()
    #m.save('ms0')
    #m.finish()

if __name__ == '__main__':
    SimpleDecoupling(SAMPLE+'_'+'')
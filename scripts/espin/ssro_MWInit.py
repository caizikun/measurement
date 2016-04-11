# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(ps)
from measurement.lib.pulsar import pulselib
reload(pulselib)
execfile(qt.reload_current_setup)

execfile(qt.reload_current_setup)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

"""
Guidelines:

Adjustment to SSRO calibration. Instead of initializing into ms = +-1 via Lasers
initialisation is done into ms = 0 followed by MW pulses.

Order of SSRO calibraiton
    1) ms = 0
    2) ms = +1
    3) ms = -1

Have MW1_frequency on ms = +1 freq (Make sure that you 
    put electron transition to +1 in msmt_params so that the MW1 freq is correct)
Have MW2_frequency on ms = -1 freq (2nd MW source can only do -1 due to its range)

Multiplicity of the pulses should be [0, 1, 1]

"""

def ssro_MWInit(name, multiplicity=[0], debug=False, mw2=[False], el_states = ['ms0'], **kw):

    m = pulsar_msmt.SSRO_MWInit(name)
    
    # Import all msmst params
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    # stools.turn_off_all_lasers()
    ### SSRO RO duration sweep params
    #### Maybe not hardcode RO time
    # m.params['SSRO_duration_list'] = np.arange(0,51,10)
    # m.params['SSRO_duration_list'] = np.linspace(0,0,10)
    

    # MW settings
    pulse_shape = kw.get('pulse_shape', None)
    if pulse_shape == None:
        pulse_shape == m.params['pulse_shape']
    else:
        m.params['pulse_shape'] = pulse_shape

    

    ### need to selectr the correct frequency
    if mw2:
        if m.params['pulse_shape'] == 'Hermite':
            print 'Using Hermite pulses'
            m.params['mw2_duration']            = m.params['mw2_Hermite_pi_length']
            m.params['mw2_pulse_amplitudes']    = m.params['mw2_Hermite_pi_amp'] 
            m.params['MW_pulse_amplitudes']     = m.params['mw2_Hermite_pi_amp'] 
        else:
            print 'Using square pulses'
            m.params['mw2_duration']            =  m.params['mw2_Square_pi_length']
            m.params['mw2_pulse_amplitudes']    = m.params['mw2_Square_pi_amp'] 
            m.params['MW_pulse_amplitudes']     = m.params['mw2_Square_pi_amp'] 
    else:
        if m.params['pulse_shape'] == 'Hermite':
            print 'Using Hermite pulses'
            m.params['MW_duration'] = m.params['Hermite_pi_length']
            m.params['MW_pulse_amplitudes'] = m.params['Hermite_pi_amp']
        else:
            print 'Using square pulses'
            m.params['MW_duration'] =  m.params['Square_pi_length']
            m.params['MW_pulse_amplitudes'] = m.params['Square_pi_amp']


    # Sweep params
    # m.params['sweep_name'] = 'SSRO_MWInit duration'
    # m.params['sweep_pts'] = m.params['SSRO_duration_list']
    m.params['wait_for_AWG_done'] = 1
    # m.params['sequence_wait_time'] = 20
    m.params['send_AWG_start'] = 1
    m.params['pts'] = 1
    
    m.params['repetitions'] = 5000
    m.params['Ex_SP_amplitude']=0

    #pick one?
    # X = ps.X_pulse(m)
    # m.generate_sequence(upload=True, pulse_pi = X)
    

    for mult, mw2, s in zip(multiplicity, mw2, el_states):
        m.params['multiplicity'] = mult
        m.MW_pi = pulse.cp(ps.pi_pulse_MW2(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
        m.autoconfig() #Already done
        m.generate_sequence(upload=True, pulse_pi = m.MW_pi)

        if not debug:
            m.run(autoconfig=False)
            print 'crash @ save'
            print s
            m.save(s)
            print 'crash @ finish'
    m.finish()

    # used to be
    # espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

    # finish(m, upload=True, debug=False, **kw):
    # m.autoconfig()
    # m.generate_sequence(upload=upload, **kw)
    # if not debug:
    #     m.run(autoconfig=False)
    #     m.save()
    #     m.finish()

    # if not debug:
    #     m.run()
    #     m.save('ms0')
    #     m.finish()


if __name__ == '__main__':

    mult = [0,1,1]
    mw2  = [False, False,True]
    el_states = ['ms0','msp1','msm1']
    debug = False

    
    ssro_MWInit(SAMPLE_CFG + '_ssro_MWInit', 
            multiplicity = mult, 
            debug = debug, 
            mw2= mw2, 
            pulse_shape='Hermite',
            el_states = el_states)

'''''
LITERAL COPIES of fidelity_SSRO_0_p1 and a class in PulsarMeasurement

Note: Adwin gets its parameters from m.params. So looping over this value will work
'''''

# """
# Script to calibrate SSRO using read-out on ms=0,+1 lines
# """
# import numpy as np
# import qt

# #reload all parameters and modules


# import measurement.lib.config.adwins as adwins_cfg
# import measurement.lib.measurement2.measurement as m2

# # import the msmt class
# from measurement.lib.measurement2.adwin_ssro import ssro
# from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# from measurement.lib.measurement2.adwin_ssro import pulse_select as ps #hermite or square?
# execfile(qt.reload_current_setup)

# SAMPLE = qt.exp_params['samples']['current']
# SAMPLE_CFG = qt.exp_params['protocols']['current']

# def fidelity_SSRO_0_p1 (name):
#     m = pulsar_msmt.SSRO_calibration_msp1(name)

#     m.params.from_dict(qt.exp_params['samples'][SAMPLE])
#     m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
#     m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
#     m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
#     m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
#     m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
#     m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
#     #m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    
#     m.params['pts'] = 1
#     pts = m.params['pts']
#     m.params['repetitions'] = 750
#     m.params['Ex_SP_amplitude']=0
#     sweep_param = 'length'

#     print m.params['pts']

#     X = ps.X_pulse(m)

#     # m.autoconfig() #Redundant because executed in m.run()? Tim
#     #m.generate_sequence()
#     m.generate_sequence(upload=True,Pi_pulse = X)
#     m.run()
#     qt.msleep(2)
#     m.save()
#     qt.msleep(2)
#     m.finish()
    

# if __name__ == '__main__':
#     fidelity_SSRO_0_p1(SAMPLE+'_'+'SIL18')

# class SSRO_calibration_msp1(PulsarMeasurement):
#     mprefix = 'SSRO_calib_msp1'

#     def autoconfig(self):
#         PulsarMeasurement.autoconfig(self)

#     def generate_sequence(self, upload=True,**kw):

        
#         # commented out. current script runs with pulse_select.py now. 20150901 NK
#         # define the necessary pulses
#         # X = pulselib.MW_IQmod_pulse('pi-pulse-on-p1',
#         #     I_channel='MW_Imod', Q_channel='MW_Qmod',
#         #     PM_channel='MW_pulsemod',
#         #     amplitude = self.params['MW_pi_msp1_amp'],
#         #     length = self.params['MW_pi_msp1_dur'],
#         #     frequency = self.params['ms+1_mod_frq'],
#         #     PM_risetime = self.params['MW_pulse_mod_risetime'])
        

#         X = kw.get('Pi_pulse', None)


#         Trig = pulse.SquarePulse(channel = 'adwin_sync', length = 10e-6, amplitude = 2)

#         T = pulse.SquarePulse(channel='MW_Imod', name='delay')
#         T.amplitude = 0.
#         T.length = 2e-6

#         # make the elements - one for each ssb frequency
#         elements = [] 
#         seq = pulsar.Sequence('SSRO calibration (ms=0,+1 RO) sequence')

#         #Nitrogen init element
#         n = element.Element('wait_time', pulsar=qt.pulsar)
#         n.append(pulse.cp(T,length=1e-6))
#         n.append(Trig)
#         elements.append(n)
#         #Spin RO element.
#         e = element.Element('pi_pulse_msm1', pulsar=qt.pulsar)
#         e.append(pulse.cp(T, length = 2e-6))
#         e.append(X)
#         e.append(Trig)
#         elements.append(e)
#         for e in elements:
#             seq.append(name=e.name, wfname=e.name, trigger_wait=True)

#          # upload the waveforms to the AWG
#         qt.pulsar.program_awg(seq,*elements)
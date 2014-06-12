"""
Script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import bell
reload(bell)
reload(eom_pulses)
import sequence as bseq
reload(bseq)
import params
reload(params)
import params_lt1
reload(params_lt1)

class Tail(bell.Bell):
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process
    
    def generate_sequence(self):
  
        self.tail_seq = pulsar.Sequence('Tail')

        elements = [] 

        for i in range(self.params['pts']):
            eom_p = self.create_eom_pulse(i)
            e = bseq._LDE_element(self, 
                name = 'Tail sweep element {}'.format(i),
               eom_pulse =  eom_p)    
            elements.append(e)
            self.tail_seq.append(name = 'Tail sweep {}'.format(i),
                wfname = e.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.params['LDE_attempts_before_CR'])
            
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.tail_seq)

    def save(self):
        pulsar_pq.PQPulsarMeasurement.save(self)

    def print_measurement_progress(self):
        pulsar_pq.PQPulsarMeasurement.print_measurement_progress(self)

    def create_eom_pulse(self, i):
        if self.params['use_eom_pulse'] == 'short':
            print 'using short eom pulse'
            return eom_pulses.EOMAOMPulse_step('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_off_duration = self.params['eom_off_duration'],
                    eom_off_amplitude = self.params['eom_off_amplitude'],
                    eom_off_2_amplitude  = 2.65, #msmt.params_lt3['eom_off_2_amplitude'],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'][i],
                    eom_overshoot1 = 0.0, #msmt.params_lt3['eom_overshoot1'],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2 = 0.0, #msmt.params_lt3['eom_overshoot2'],
                    aom_risetime = self.params['aom_risetime'][i]) 
        elif self.params['use_eom_pulse'] == 'raymond-pulse':
            return eom_pulses.EOMAOMPulse_raymond_pulse('Eom Aom Pulse', 
                    eom_channel             = 'EOM_Matisse',
                    aom_channel             = 'EOM_AOM_Matisse',
                    eom_trigger_channel     = 'EOM_trigger',
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_comp_pulse_amplitude= self.params['eom_comp_pulse_amplitude'][i],
                    eom_trigger_duration      = self.params['eom_trigger_duration'],
                    eom_trigger_pulse_duration= self.params['eom_trigger_pulse_duration'],
                    eom_trigger_amplitude   = self.params['eom_trigger_amplitude'],
                    aom_risetime            = self.params['aom_risetime'][i],
                    aom_amplitude           = self.params['aom_amplitude'][i])
        elif self.params['use_eom_pulse'] == 'raymond-step':
            return eom_pulses.EOMAOMPulse_raymond_step('Eom Aom Pulse', 
                    eom_channel             = 'EOM_Matisse',
                    aom_channel             = 'EOM_AOM_Matisse',
                    eom_trigger_channel     = 'EOM_trigger',
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_comp_pulse_amplitude= self.params['eom_comp_pulse_amplitude'][i],
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_trigger_amplitude   = self.params['eom_trigger_amplitude'],
                    aom_risetime            = self.params['aom_risetime'][i],
                    aom_amplitude           = self.params['aom_amplitude'][i])
        else: 
            return eom_pulses.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_off_duration        = self.params['eom_off_duration'],
                    eom_off_amplitude       = self.params['eom_off_amplitude'][i],
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'][i],
                    eom_overshoot1          = self.params['eom_overshoot1'][i],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2          = self.params['eom_overshoot2'],
                    aom_risetime            = self.params['aom_risetime'][i],
                    aom_amplitude           = self.params['aom_amplitude'][i])

Tail.bs_helper = qt.instruments['bs_helper']
def tail_lt3(name):

    m=Tail(name)

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])

    m.joint_params = {}
    for k in params.params_lt3:
        m.params[k] = params.params_lt3[k]
    for k in params.joint_params:
        m.params[k] = params.joint_params[k]
        m.joint_params[k] = params.joint_params[k]

    pts=10
    m.params['pts']=pts
    
    #EOM pulse ----------------------------------
    #qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 147e-9)
    #qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0

    m.params['use_eom_pulse'] = 'normal'#raymond-step' #'short', 'raymond-pulse', 'raymond-step'
    m.params['eom_off_amplitude']         = np.ones(pts)*-0.07#np.linspace(-0.1,0.05,pts) # calibration from 19-03-2014
    m.params['aom_risetime']              = np.ones(pts)*25e-9 # calibration to be done!
   
    if m.params['use_eom_pulse'] == 'raymond-pulse':

        m.params['eom_pulse_amplitude']         = np.ones(pts)*1.45 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']          = np.ones(pts)* 60e-9
        m.params['eom_trigger_duration']        = 80e-9
        m.params['eom_trigger_pulse_duration']  = 1e-9
        m.params['eom_trigger_amplitude']       = 1.0
        m.params['eom_comp_pulse_amplitude']    = (m.params['eom_trigger_duration']*m.params['eom_off_amplitude'] \
                                                    +m.params['eom_trigger_pulse_duration']*m.params['eom_pulse_amplitude'] )/m.params['eom_pulse_duration']  
    elif m.params['use_eom_pulse'] == 'raymond-step': 

        m.params['eom_pulse_amplitude']        = np.ones(pts)*2.9 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']         = np.ones(pts)* 100e-9
        m.params['eom_trigger_amplitude']      = 1.0
        m.params['eom_comp_pulse_amplitude']   = (0.5*m.params['eom_pulse_duration']*m.params['eom_pulse_amplitude'] \
                                                    +m.params['eom_pulse_duration']*m.params['eom_off_amplitude'] )/(2.*m.params['eom_pulse_duration'])  
    else:#'normal':

        m.params['eom_pulse_amplitude']        = np.ones(pts)*2.0 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']         = np.ones(pts)*2e-9
        m.params['eom_comp_pulse_amplitude']   = m.params['eom_pulse_amplitude'] 
        m.params['eom_off_duration']           = 200e-9
        m.params['eom_overshoot_duration1']    = np.ones(pts)*10e-9
        m.params['eom_overshoot1']             = np.ones(pts)*-0.03 # calibration from 19-03-2014# 
        m.params['eom_overshoot_duration2']    = 10e-9
        m.params['eom_overshoot2']             = 0
        m.params['eom_aom_on']                = True
    
    p_aom= qt.instruments['PulseAOM']
    max_power_aom=p_aom.voltage_to_power(p_aom.get_V_max())
    aom_power_sweep=linspace(0.2,0.6,pts)*max_power_aom #%power
    aom_voltage_sweep = np.zeros(pts)
    for i,p in enumerate(aom_power_sweep):
        aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

    m.params['aom_amplitude'] = aom_voltage_sweep #np.ones(pts)*1.0#aom_voltage_sweep 

    m.params['sweep_name'] = 'aom_amplitude [percent]'
    m.params['sweep_pts'] = aom_power_sweep/max_power_aom

    bseq.pulse_defs_lt3(m)
    m.params['MIN_SYNC_BIN'] =       5000 
    m.params['MAX_SYNC_BIN'] =       7000

    m.params['send_AWG_start'] = 1
    m.params['syncs_per_sweep'] = m.params['LDE_attempts_before_CR']
    m.params['repetitions'] = 10000
    m.params['SP_duration'] = 250

    m.joint_params['opt_pi_pulses'] = 1
    m.joint_params['RO_during_LDE'] = 0
    m.params['MW_during_LDE'] = 0
    
    debug=False
    measure_bs=True

    m.params['trigger_wait'] = True#not(debug)
    m.autoconfig()
    m.generate_sequence()
    #print m.params['measurement_time']

    if measure_bs:
            m.bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_bs.py')
            m.bs_helper.set_measurement_name(name)
            m.bs_helper.set_is_running(True)
            m.bs_helper.execute_script()

    m.setup(debug=(debug or measure_bs))
    m.run(autoconfig=False, setup=False,debug=(debug or measure_bs))    
    m.save()
    if measure_bs:
        m.bs_helper.set_is_running(False)
        m.params['bs_data_path'] = m.bs_helper.get_data_path()
    m.finish()


def tail_lt1(name):

    m=Tail(name)

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])

    m.joint_params = {}
    for k in params_lt1.params_lt1:
        m.params[k] = params_lt1.params_lt1[k]
    for k in params.joint_params:
        m.params[k] = params.joint_params[k]
        m.joint_params[k] = params.joint_params[k]

    pts=10
    m.params['pts']=pts
    
    #EOM pulse ----------------------------------
    #qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 147e-9)
    #qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0

    m.params['use_eom_pulse'] = 'normal'#raymond-step' #'short', 'raymond-pulse', 'raymond-step'
    m.params['eom_off_amplitude']         = np.ones(pts)*-0.375#np.linspace(-0.1,0.05,pts) # calibration from 19-03-2014
    m.params['aom_risetime']              = np.ones(pts)*38e-9#42e-9 # calibration to be done!
   
    if m.params['use_eom_pulse'] == 'raymond-pulse':

        m.params['eom_pulse_amplitude']         = np.ones(pts)*1.45 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']          = np.ones(pts)* 60e-9
        m.params['eom_trigger_duration']        = 80e-9
        m.params['eom_trigger_pulse_duration']  = 1e-9
        m.params['eom_trigger_amplitude']       = 1.0
        m.params['eom_comp_pulse_amplitude']    = (m.params['eom_trigger_duration']*m.params['eom_off_amplitude'] \
                                                    +m.params['eom_trigger_pulse_duration']*m.params['eom_pulse_amplitude'] )/m.params['eom_pulse_duration']  
    elif m.params['use_eom_pulse'] == 'raymond-step': 

        m.params['eom_pulse_amplitude']        = np.ones(pts)*2.9 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']         = np.ones(pts)* 100e-9
        m.params['eom_trigger_amplitude']      = 1.0
        m.params['eom_comp_pulse_amplitude']   = (0.5*m.params['eom_pulse_duration']*m.params['eom_pulse_amplitude'] \
                                                    +m.params['eom_pulse_duration']*m.params['eom_off_amplitude'] )/(2.*m.params['eom_pulse_duration'])  
    else:#'normal':

        m.params['eom_pulse_duration']         = np.ones(pts)* 2e-9
        m.params['eom_pulse_amplitude']        = np.ones(pts)*2.0
        m.params['eom_comp_pulse_amplitude']   = m.params['eom_pulse_amplitude'] 
        m.params['eom_off_duration']           = 200e-9
        m.params['eom_overshoot_duration1']    = np.linspace(1e-9,15e-9,pts)
        m.params['eom_overshoot1']             = np.ones(pts)*-0.05  #     np.ones(pts)*-0.03 # calibration from 19-03-2014# 
        m.params['eom_overshoot_duration2']    = 10e-9
        m.params['eom_overshoot2']             = 0
        m.params['eom_aom_on']                = True
    
    p_aom= qt.instruments['PulseAOM']
    max_power_aom=p_aom.voltage_to_power(p_aom.get_V_max())
    aom_power_sweep=linspace(0.2,1.0,pts)*max_power_aom #%power
    aom_voltage_sweep = np.zeros(pts)
    for i,p in enumerate(aom_power_sweep):
        aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

    m.params['aom_amplitude']             = aom_voltage_sweep#np.ones(pts)*1.0#aom_voltage_sweep 

    m.params['sweep_name'] = 'sqrt aom power'
    m.params['sweep_pts'] = np.sqrt(aom_power_sweep/max_power_aom)

    bseq.pulse_defs_lt1(m)
    m.params['MIN_SYNC_BIN'] =       6000 
    m.params['MAX_SYNC_BIN'] =       8000

    m.params['sync_during_LDE'] = 1
    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['syncs_per_sweep'] = m.params['LDE_attempts_before_CR']
    m.params['repetitions'] = 15000
    m.params['SP_duration'] = 250

    m.joint_params['opt_pi_pulses'] = 1
    m.joint_params['RO_during_LDE'] = 0
    m.params['MW_during_LDE'] = 0
    
    debug=False
    measure_bs=True

    m.params['trigger_wait'] = 1
    m.autoconfig()
    m.generate_sequence()

    if measure_bs:
            m.bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_bs.py')
            m.bs_helper.set_measurement_name(name)
            m.bs_helper.set_is_running(True)
            m.bs_helper.execute_script()


    m.setup(debug=(debug or measure_bs))
    m.run(autoconfig=False, setup=False,debug=(debug or measure_bs))    
    m.save()
    if measure_bs:
        m.bs_helper.set_is_running(False)
        m.params['bs_data_path'] = m.bs_helper.get_data_path()
    m.finish()

if __name__ == '__main__':
    tail_lt3('lt3_Sam_Sil5')

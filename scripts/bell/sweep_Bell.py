"""
Script for sweeping a parameter in the Bell sequence.
The detection is done with a picoquant time correlator
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
import joint_params
reload(joint_params)
import params_lt3
reload(params_lt3)
import params_lt1
reload(params_lt1)

class SweepBell(bell.Bell):
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process
    
    def generate_sequence(self):
  
        self.sweep_bell_seq = pulsar.Sequence('Bell_sweep')

        elements = [] 

        for i in range(self.params['pts']):
            if self.params['do_general_sweep'] :
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i]

            if self.params['setup'] == 'lt3':
                bseq.pulse_defs_lt3(self)
            elif self.params['setup'] == 'lt1':
                bseq.pulse_defs_lt1(self)    

            eom_p = self.create_eom_pulse(i)
            LDE_element = bseq._LDE_element(self, 
                name = 'Bell sweep element {}'.format(i),
                eom_pulse =  eom_p)    
            elements.append(LDE_element)

            if self.joint_params['wait_for_1st_revival']:
                LDE_echo_point = LDE_element.length()- (LDE_element.pulses['MW_pi'].effective_start()+ self.params['MW_1_separation'])
                late_RO_element = bseq._1st_revival_RO(self, LDE_echo_point = LDE_echo_point, name = 'late RO element {}'.format(i))
                elements.append(late_RO_element)
            
            self.sweep_bell_seq.append(name = 'Bell sweep {}'.format(i),
                wfname = LDE_element.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.joint_params['LDE_attempts_before_CR'])

            if self.joint_params['wait_for_1st_revival']:
                self.sweep_bell_seq.append(name= 'late_RO {}'.format(i),
                    wfname = late_RO_element.name )

            
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.sweep_bell_seq)
        #qt.pulsar.program_awg(self.sweep_bell_seq,*elements)

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
        elif self.params['use_eom_pulse'] == 'original':
            return eom_pulses.OriginalEOMAOMPulse('Eom Aom Pulse', 
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

SweepBell.bs_helper = qt.instruments['bs_helper']

def sweep_bell(name, setup = 'lt3'):

    m=SweepBell(name)

    m.params['setup'] = setup

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])

    #m.joint_params = {}
    for k in joint_params.joint_params:
        m.joint_params[k] = joint_params.joint_params[k]

    if setup == 'lt3' :
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt3.params_lt3:
            m.params[k] = params_lt3.params_lt3[k]

    elif setup == 'lt1' :
        m.AWG_RO_AOM = m.E_aom
        for k in params_lt1.params_lt1:
            m.params[k] = params_lt1.params_lt1[k]

        m.params['sync_during_LDE'] = 1
        m.params['wait_for_AWG_done'] = 0

    pts=11
    m.params['pts']=pts
    
    
    #EOM pulse ----------------------------------
    #qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 147e-9)
    #qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0

    m.params['use_eom_pulse'] = 'original' #normal'#raymond-step' #'short', 'raymond-pulse', 'raymond-step'
    
    if setup == 'lt3' :
        m.params['eom_off_amplitude']         = np.ones(pts)*-0.055 #calibration from 2014-07-23
        m.params['aom_risetime']              = np.ones(pts)*15e-9 # 
    elif setup == 'lt1' :
        m.params['eom_off_amplitude']         = np.ones(pts)*-0.265#np.linspace(-0.35,-0.2,pts) #np.ones(pts)*-0.28# calibration from 19-03-2014
        m.params['aom_risetime']              = np.ones(pts)*35e-9#38e-9#42e-9 # calibration to be done!

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

        if setup == 'lt3':
            m.params['eom_pulse_amplitude']        = np.ones(pts)*2.0 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
            m.params['eom_overshoot_duration1']    = np.ones(pts)*20e-9
            m.params['eom_overshoot1']             = np.ones(pts)*-0.03 # calibration from 19-03-2014# 
        elif setup == 'lt1': 
            m.params['eom_pulse_amplitude']        = np.ones(pts)*1.9
            m.params['eom_overshoot_duration1']    = np.ones(pts)*20e-9#10e-9 #what is the correct value ?
            m.params['eom_overshoot1']             = np.ones(pts)*-0.04  #  calibration from 22-07-2014# 

        m.params['eom_pulse_duration']         = np.ones(pts)*2e-9
        m.params['eom_comp_pulse_amplitude']   = m.params['eom_pulse_amplitude'] 
        m.params['eom_off_duration']           = 150e-9
        m.params['eom_overshoot_duration2']    = 10e-9
        m.params['eom_overshoot2']             = 0


    

    do_tail = True
    do_sweep_aom_power = True
    if do_tail:
        m.joint_params['LDE_attempts_before_CR'] = 250
        m.params['LDE_attempts_before_CR'] = 250
        m.params['do_general_sweep']= 0
        m.joint_params['opt_pi_pulses'] = 1
        m.joint_params['RND_during_LDE'] = 0
        m.joint_params['RO_during_LDE'] = 0
        m.params['MW_during_LDE'] = 0
        m.joint_params['RND_during_LDE'] = 0
        m.joint_params['LDE_element_length'] = 7e-6
        m.joint_params['do_final_MW_rotation'] = 0
        m.joint_params['wait_for_1st_revival'] = 0

        if do_sweep_aom_power:
            p_aom= qt.instruments['PulseAOM']
            aom_voltage_sweep = np.zeros(pts)
            max_power_aom=p_aom.voltage_to_power(p_aom.get_V_max())
            aom_power_sweep=linspace(0.3,0.8,pts)*max_power_aom #%power
            for i,p in enumerate(aom_power_sweep):
                aom_voltage_sweep[i]= p_aom.power_to_voltage(p)
            m.params['aom_amplitude'] = aom_voltage_sweep
            m.params['sweep_name'] = 'aom power (percentage/max_power_aom)' 
            m.params['sweep_pts'] = aom_power_sweep/max_power_aom
        else:
            m.params['aom_amplitude'] = np.ones(pts)*0.7 #np.linspace(0.6,1.0,pts)
            m.params['sweep_name'] = 'eom off amplitude (V)' #aom power (percentage/max_power_aom)' 
            m.params['sweep_pts'] = m.params['eom_off_amplitude']#aom_power_sweep/max_power_aom

    else : 
        m.params['do_general_sweep']= 1# sweep the parameter defined by general_sweep_name, with the values given by general_sweep_pts
        m.params['general_sweep_name'] = 'echo_offset' 
        m.params['general_sweep_pts'] = np.linspace(-100e-9,100e-9,pts)
        m.joint_params['DD_number_pi_pulses'] = 2
        m.params['free_precession_offset'] = 0e-9
        m.joint_params['do_echo'] = 1

        #if np.mod(m.joint_params['DD_number_pi_pulses'],2) == 0 :
        #    m.params['echo_offset'] = 0.e-9
        #print 'The echo ffset is set to {} ns.'.format(m.params['echo_offset']*1e9)
        if np.mod(m.joint_params['DD_number_pi_pulses'],2) == 0 :
            m.params['echo_offset'] = 0.e-9

        m.joint_params['LDE_attempts_before_CR'] = 1
        m.joint_params['opt_pi_pulses'] = 2
        m.params['aom_amplitude'] = np.ones(pts)*0. #0.88

        m.joint_params['RND_during_LDE'] = 1
        m.joint_params['RO_during_LDE'] = 1
        m.params['MW_during_LDE'] = 1 # the maximum number of pi pulses is 3 !!!
        m.joint_params['do_final_MW_rotation'] = 1

        # to measure the echo on the 1st revival
        # 2 parameters can be swept : free_precession_time_1st_revival and echo_offset
        m.joint_params['wait_for_1st_revival'] = 0

        #for the analysis:
        m.params['sweep_name'] = m.params['general_sweep_name']# 'free_precession_time_1st_revival'#'aom voltage' 
        m.params['sweep_pts'] = m.params['general_sweep_pts']
    
    print 'sweep points : ', m.params['sweep_pts']
    

    m.params['syncs_per_sweep'] = m.joint_params['LDE_attempts_before_CR']  

    m.params['MIN_SYNC_BIN'] =       5000 
    m.params['MAX_SYNC_BIN'] =       16000 # for Bell, 16000

    m.params['send_AWG_start'] = 1    
    m.params['repetitions'] = 5000

    th_debug=False
    measure_bs=False
    upload_only = False

    m.params['trigger_wait'] = True#not(debug)
    m.autoconfig()
    m.generate_sequence()
    if upload_only:
        return
    if measure_bs:
            m.bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_bs.py')
            m.bs_helper.set_measurement_name(name)
            m.bs_helper.set_is_running(True)
            m.bs_helper.execute_script()
    m.setup(debug=th_debug)
    m.run(autoconfig=False, setup=False,debug=th_debug)    
    m.save()
    if measure_bs:
        m.bs_helper.set_is_running(False)
        m.params['bs_data_path'] = m.bs_helper.get_data_path()
    
    m.finish()



if __name__ == '__main__':
    sweep_bell('Samy_Tail_PSB_10deg', setup = 'lt3')    

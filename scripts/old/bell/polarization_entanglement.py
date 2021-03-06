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
import pol_sequence as bseq
reload(bseq)

class Polarization_entanglement(bell.Bell):
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process
    
    def generate_sequence(self):
  
        self.sweep_bell_seq = pulsar.Sequence('Pol_Entanglement')

        elements = [] 

        for i in range(self.params['pts']):
            if self.params['do_general_sweep'] :
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i]

            if self.params['setup'] == 'lt4':
                bseq.pulse_defs_lt4(self)
            elif self.params['setup'] == 'lt3':
                bseq.pulse_defs_lt3(self)    

            LDE_element = bseq._LDE_element(self, 
                name = 'Bell sweep element {}'.format(i))    
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

    #def run(self,**kw):
    #    pulsar_pq.PQPulsarMeasurement.run(self, **kw)

    def print_measurement_progress(self):
        pulsar_pq.PQPulsarMeasurement.print_measurement_progress(self)

Polarization_entanglement.bs_helper = qt.instruments['bs_helper']

def _setup_params(msmt, setup):
    msmt.params['setup']=setup
    msmt.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    msmt.params.from_dict(qt.exp_params['protocols']['cr_mod'])

    
    if not(hasattr(msmt,'joint_params')):
        msmt.joint_params = {}
    import joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        msmt.joint_params[k] = joint_params.joint_params[k]

    if setup == 'lt4' :
        import params_lt4
        reload(params_lt4)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            msmt.params[k] = params_lt4.params_lt4[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt4(msmt)
    elif setup == 'lt3' :
        import params_lt3
        reload(params_lt3)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt3.params_lt3:
            msmt.params[k] = params_lt3.params_lt3[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt3(msmt)
    else:
        print 'Sweep_bell: invalid setup:', setup

    msmt.params['send_AWG_start'] = 1
    msmt.params['sync_during_LDE'] = 1
    msmt.params['wait_for_AWG_done'] = 0
    msmt.params['do_general_sweep']= 1
    msmt.params['trigger_wait'] = 1




###########################################################################
###########################measurements####################################
###########################################################################

def tail_sweep(name):
    m=Polarization_entanglement('tail_sweep'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=11
    m.params['pts']=pts
    m.params['repetitions'] = 500 #
    m.params['LDE_SP_duration'] = 5e-6
    m.params['opt_pulse_start'] = 0.5e-6
    m.joint_params['LDE_attempts_before_CR'] = 250
    m.joint_params['DD_number_pi_pulses'] = 0
    m.joint_params['opt_pi_pulses'] = 1
    m.params['opt_pulse_start'] = 2e-6
    m.joint_params['opt_pulse_separation'] = 0.6e-6
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 0
    m.params['MW_during_LDE'] = 1
    m.params['MW_PiInit_Delay'] = 1e-6
    m.params['Spin_Init_MW'] = False
    m.joint_params['LDE_element_length'] = 16e-6
    m.joint_params['do_final_MW_rotation'] = 0
    m.joint_params['wait_for_1st_revival'] = 0

    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       16000 

    do_sweep_aom_power = True
    if do_sweep_aom_power:
        p_aom= qt.instruments['PulseAOM']
        aom_voltage_sweep = np.zeros(pts)
        max_power_aom=p_aom.voltage_to_power(1.)
        aom_power_sweep=np.linspace(0.01,1,pts)*max_power_aom #%power 
        for i,p in enumerate(aom_power_sweep):
            aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

        m.params['general_sweep_name'] = 'aom_amplitude' 
        m.params['general_sweep_pts'] = aom_voltage_sweep
        m.params['sweep_name'] = 'aom power (percentage/max_power_aom)' 
        m.params['sweep_pts'] = aom_power_sweep/max_power_aom
    else:
        sweep_off_voltage = False
        if sweep_off_voltage:
            m.params['general_sweep_name'] = 'eom_off_amplitude'
            print 'sweeping the', m.params['general_sweep_name']
            m.params['general_sweep_pts'] = np.linspace(-0.25,-0.35,pts)
            m.params['sweep_name'] = m.params['general_sweep_name'] 
            m.params['sweep_pts'] = m.params['general_sweep_pts']
        else:
            m.params['general_sweep_name'] = 'aom_amplitude'
            print 'sweeping the', m.params['general_sweep_name']
            m.params['general_sweep_pts'] = np.linspace(0.01,1.,pts)
            m.params['sweep_name'] = m.params['general_sweep_name'] 
            m.params['sweep_pts'] = m.params['general_sweep_pts']


    run_sweep(m, th_debug=False, measure_bs=False, upload_only = False)

def pol_entanglement(name):
    m=Polarization_entanglement('pol_entanglement'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=1
    m.params['pts']=pts
    m.params['repetitions'] = 100000 #
    m.params['LDE_SP_duration'] = 5e-6
    m.params['opt_pulse_start'] = 0.5e-6
    m.joint_params['LDE_attempts_before_CR'] = 250
    m.joint_params['DD_number_pi_pulses'] = 0
    m.joint_params['opt_pi_pulses'] = 1
    m.params['opt_pulse_start'] = 1e-6
    m.joint_params['opt_pulse_separation'] = 0.6e-6
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 1
    m.joint_params['LDE_RO_duration'] = 10e-6
    m.params['RO_wait'] = 3e-6
    m.params['MW_1_separation']= 1e-6
    m.params['MW_during_LDE'] = 1
    m.params['MW_PiInit_Delay'] = 1e-6
    m.params['Spin_Init_MW'] = False
    m.joint_params['LDE_element_length'] = 20e-6
    m.joint_params['do_final_MW_rotation'] = 0
    m.joint_params['wait_for_1st_revival'] = 0

    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       20000 

    p_aom= qt.instruments['PulseAOM']
    aom_voltage_sweep = np.zeros(pts)
    max_power_aom=p_aom.voltage_to_power(1.)
    aom_power_sweep=np.linspace(1.,1.,pts)*max_power_aom #%power 
    for i,p in enumerate(aom_power_sweep):
        aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

    m.params['general_sweep_name'] = 'aom_amplitude' 
    m.params['general_sweep_pts'] = aom_voltage_sweep
    m.params['sweep_name'] = 'aom power (percentage/max_power_aom)' 
    m.params['sweep_pts'] = aom_power_sweep/max_power_aom


    run_sweep(m, th_debug=False, measure_bs=False, upload_only = False)


def echo_sweep(name):
    print 'setting up the echo sweep'
    m=Polarization_entanglement('echo_sweep_'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=10
    m.params['pts']=pts
    m.params['repetitions'] = 5000
    
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 0
    m.params['MW_during_LDE'] = 1 

    m.joint_params['LDE_attempts_before_CR'] = 1
    m.params['aom_amplitude'] = 0. #
    m.joint_params['do_echo'] = 1
    m.params['Spin_Init_MW'] = False
    m.params['MW_RND_amp_I']     = -m.params['MW_pi2_amp']
    m.params['MW_RND_duration_I']= m.params['MW_pi2_duration'] 
    m.params['MW_RND_amp_Q']     = -m.params['MW_pi2_amp']
    m.params['MW_RND_duration_Q']= m.params['MW_pi2_duration']
    m.joint_params['LDE_element_length']=20e-6

    # 2 parameters can be swept : free_precession_time_1st_revival and echo_offset
    # see PPT 2014-07-14_DataMeeting_PulseCalibration for scheme
    m.joint_params['wait_for_1st_revival'] = 0 # to measure the echo on the 1st revival

    m.params['free_precession_offset'] = 0e-9
    m.params['echo_offset'] = -50e-9
    m.params['general_sweep_name'] = 'echo_offset'
    m.params['general_sweep_pts'] = np.linspace(-150e-9, 20e-9, pts)

    #for the analysis:
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    run_sweep(m, th_debug=False, measure_bs=False, upload_only = False)

def spinpumping_sweep(name):
    m=Polarization_entanglement('_'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=1
    m.params['pts']=pts
    m.params['repetitions'] = 10000 # 

    m.joint_params['LDE_attempts_before_CR'] = 250
    m.joint_params['opt_pi_pulses'] = 2
    m.params['aom_amplitude'] = 0. # no optical pulses
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 1
    m.params['MW_during_LDE'] = 1
    m.joint_params['LDE_element_length'] = 15e-6
    m.joint_params['do_final_MW_rotation'] = 1
    m.joint_params['wait_for_1st_revival'] = 0

    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       15000 

    m.params['general_sweep_name'] = 'LDE_SP_duration'
    m.params['general_sweep_pts'] = np.linspace(4.9e-6, 5e-6, pts)
    #for the analysis:
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    run_sweep(m, th_debug=False, measure_bs=False, upload_only = False)

def num_decoupling_pulses_sweep(name):
    m=Polarization_entanglement('num_decoupling_pulses_sweep_'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=1
    m.params['pts']=pts
    m.params['repetitions'] = 5000
    
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 0
    m.params['MW_during_LDE'] = 1 

    m.joint_params['LDE_attempts_before_CR'] = 1
    m.params['aom_amplitude'] = 0. #
    m.joint_params['do_echo'] = 1
    m.params['MW_RND_amp_I']     = m.params['MW_pi2_amp']
    m.params['MW_RND_duration_I']= m.params['MW_pi2_duration'] 
    m.params['MW_RND_amp_Q']     = m.params['MW_pi2_amp']
    m.params['MW_RND_duration_Q']= m.params['MW_pi2_duration']
    m.joint_params['wait_for_1st_revival'] = 1 # to measure the echo on the 1st revival
    m.joint_params['DD_number_pi_pulses'] =10
    m.params['free_precession_offset'] = 0e-9
    m.params['echo_offset'] = -50e-9
    m.params['general_sweep_name'] = 'DD_number_pi_pulses'
    m.params['general_sweep_pts'] = np.linspace(1, 5, pts)

    #for the analysis:
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    run_sweep(m, th_debug=True, measure_bs=False, upload_only = False)


def run_sweep(m, th_debug=False, measure_bs=True, upload_only = False):
    m.autoconfig()
    m.generate_sequence()
    if upload_only:
        return
    if measure_bs:
            m.bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_bs.py')
            m.bs_helper.set_measurement_name(m.name)
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
    SAMPLE_CFG = qt.exp_params['protocols']['current']
    pol_entanglement('Ex_RotatingHalf_65deg')
    #tail_sweep('tail') 
    #spinpumping_sweep('spinpumping')
    #echo_sweep('PippinSil1')
    #num_decoupling_pulses_sweep('PippinSil1_10Pulses')
    #rnd_echo_ro('SAMPLE_CFG_'+str(qt.bell_name_index))

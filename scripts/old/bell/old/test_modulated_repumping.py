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
import Modulated_Repumping_Sequence as bseq
reload(bseq)

class Test_modulated_repumping(bell.Bell):
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process
    
    def generate_sequence(self):
  
        self.sweep_bell_seq = pulsar.Sequence('Modulated_Repumping_Sequence')

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

Test_modulated_repumping.bs_helper = qt.instruments['bs_helper']

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


def test_it_now(name):
    m=Test_modulated_repumping('modulated_repumping'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=1
    m.params['pts']=pts
    m.params['repetitions'] = 10000 #
    m.params['LDE_SP_duration'] = 3000e-9
    m.joint_params['LDE_attempts_before_CR'] = 100
    m.joint_params['DD_number_pi_pulses'] = 0
    m.joint_params['opt_pi_pulses'] = 2
    m.params['opt_pulse_start'] = 0e-6
    m.joint_params['opt_pulse_separation'] = 5.e-6
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['RO_during_LDE'] = 1
    m.joint_params['LDE_RO_duration'] = 8e-6
    m.params['RO_wait'] = 7e-6
    m.params['MW_1_separation']= 1e-6
    m.params['MW_during_LDE'] = 1
    m.params['MW_PiInit_Delay'] = 10.e-6
    m.params['Spin_Init_MW'] = False
    m.joint_params['LDE_element_length'] = 15e-6
    m.joint_params['do_final_MW_rotation'] = 0
    m.joint_params['wait_for_1st_revival'] = 0

    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       15000 

    pulse_delay_sweep = np.linspace(-20e-9,1480e-9,pts) 
    print 'params ', pulse_delay_sweep

    m.params['general_sweep_name'] = 'opt_pulse_start' 
    m.params['general_sweep_pts'] = pulse_delay_sweep
    m.params['sweep_name'] = 'opt_pulse_start' 
    m.params['sweep_pts'] = pulse_delay_sweep


    run_sweep(m, th_debug=False, measure_bs=False, upload_only = False)


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
    test_it_now('SingletSweep_')

"""
LT3 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import inspect
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
reload(eom_pulses)
import bell
reload(bell)
import sequence as bseq
reload(bseq)
import params
reload(params)

class Bell_LT3(bell.Bell):
    mprefix = 'Bell_LT3'

    def __init__(self, name):
        bell.Bell.__init__(self,name)
        for k in params.joint_params:
            self.joint_params[k] = params.joint_params[k]
        for k in params.params_lt3:
            self.params[k] = params.params_lt3[k]
        bseq.pulse_defs_lt3(self)

    def generate_sequence(self):
        seq = pulsar.Sequence('BellLT3')

        elements = [] 

        dummy_element = bseq._dummy_element(self)
        #finished_element = bseq._sequence_finished_element(self)
        start_element = bseq._lt3_sequence_start_element(self)
        elements.append(start_element)
        #elements.append(finished_element)
        elements.append(dummy_element)
        LDE_element = bseq._LDE_element(self, name='LDE_LT3')   
        elements.append(LDE_element)

        if self.joint_params['wait_for_1st_revival']:
            LDE_echo_point = LDE_element.length()- (LDE_element.pulses['MW_pi'].effective_start()+ self.params['MW_1_separation'])
            late_RO = bseq._1st_revival_RO(self, LDE_echo_point = LDE_echo_point, name = '1st_revival_RO_LT3')
            elements.append(late_RO)


        seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_element.name)

        seq.append(name = 'LDE_LT3',
            wfname = LDE_element.name,
            jump_target = 'late_RO' if self.joint_params['wait_for_1st_revival'] else 'RO_dummy',
            goto_target = 'start_LDE',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        #seq.append(name = 'LDE_timeout',
        #    wfname = finished_element.name,
        #    goto_target = 'start_LDE')
        if self.joint_params['wait_for_1st_revival']:
            seq.append(name = 'late_RO',
                wfname = late_RO.name,
                goto_target = 'start_LDE')

        seq.append(name = 'RO_dummy',
            wfname = dummy_element.name,
            goto_target = 'start_LDE')
            
        #qt.pulsar.program_awg(seq,*elements)
        qt.pulsar.upload(*elements) 
        qt.pulsar.program_sequence(seq)

    def stop_measurement_process(self):
        bell.Bell.stop_measurement_process(self)

        # signal BS and LT1 to stop as well
        if self.bs_helper != None:
            self.bs_helper.set_is_running(False)
        if self.lt1_helper != None:    
            self.lt1_helper.set_is_running(False)

    def reset_plu(self):
        self.adwin.start_set_dio(dio_no=2, dio_val=0)
        qt.msleep(0.1)
        self.adwin.start_set_dio(dio_no=2, dio_val=1)
        qt.msleep(0.1)
        self.adwin.start_set_dio(dio_no=2, dio_val=0)

    def finish(self):
        bell.Bell.finish(self)
        self.add_file(inspect.getsourcefile(bseq))

Bell_LT3.bs_helper = qt.instruments['bs_helper']
Bell_LT3.lt1_helper = qt.instruments['lt1_helper']

def full_bell(name):

    th_debug = True
    sequence_only = False
    mw = True
    measure_lt1 = False
    measure_bs = True
    do_upload = True

    m=Bell_LT3(name) 

    m.params['MW_during_LDE'] = mw
    m.params['wait_for_remote_CR'] = measure_lt1


    if not(sequence_only):
        if measure_lt1:
            m.lt1_helper.set_is_running(False)
            m.lt1_helper.set_measurement_name(name)
            m.lt1_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_lt1.py')
            m.lt1_helper.execute_script()
        if measure_bs:
            m.bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bell/bell_bs.py')
            m.bs_helper.set_measurement_name(name)
            m.bs_helper.set_is_running(True)
            m.bs_helper.execute_script()
    
    m.autoconfig()
    if do_upload:
        m.generate_sequence()
    if sequence_only: 
        return

    m.setup(debug=th_debug)
    m.reset_plu()

    if measure_lt1: m.lt1_helper.set_is_running(True)
    m.run(autoconfig=False, setup=False,debug=th_debug)
    m.save()

    if measure_lt1:
         m.params['lt1_data_path'] = m.lt1_helper.get_data_path()
    if measure_bs:
        m.params['bs_data_path'] = m.bs_helper.get_data_path()

    m.finish()

if __name__ == '__main__':
    full_bell('SP_corr_MW_Qmod')   
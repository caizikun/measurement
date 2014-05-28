"""
LT3 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)


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

    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s readout repetitions' % reps_completed)

    def generate_sequence(self):
        seq = pulsar.Sequence('BellLT3')

        elements = [] 

        dummy_element = bseq._dummy_element(self)
        #finished_element = bseq._sequence_finished_element(self)
        start_element = bseq._lt3_sequence_start_element(self)
        elements.append(start_element)
        #elements.append(finished_element)
        elements.append(dummy_element)
        LDE_element = bseq._LDE_element(self)   
        elements.append(LDE_element)
        
        seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_element.name)

        seq.append(name = 'LDE_LT3',
            wfname = LDE_element.name,
            jump_target = 'RO_dummy',
            goto_target = 'start_LDE',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        #seq.append(name = 'LDE_timeout',
        #    wfname = finished_element.name,
        #    goto_target = 'start_LDE')

        seq.append(name = 'RO_dummy',
            wfname = dummy_element.name,
            goto_target = 'start_LDE')
            
        qt.pulsar.program_awg(seq,*elements)

    def stop_measurement_process(self):
        bell.Bell.stop_measurement_process(self)
        # signal LT1 to stop as well
        self.remote_bs_measurement_helper.set_is_running(False)
        #TODO! self.remote_lt1_measurement_helper.set_is_running(False)

Bell_LT3.remote_bs_measurement_helper = qt.instruments['bs_helper']
Bell_LT3.remote_lt1_measurement_helper = qt.instruments['lt1_helper']

def bell_lt3(name):
    upload_only=False
    debug=True
    mw = False
    local_only = True

    m=Bell_LT3(name) 
    m.params['MW_during_LDE'] = mw
    m.params['wait_for_remote_CR'] = not(local_only)
    m.autoconfig()
    m.generate_sequence()
    
    if not(upload_only):
        m.setup(debug=debug)
        m.run(autoconfig=False, setup=False,debug=debug)    
        m.save()
        m.finish()

if __name__ == '__main__':
    bell_lt3('test')
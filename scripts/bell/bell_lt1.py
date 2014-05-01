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
import params_lt1
import params
reload(params_lt1)
reload(params)

class Bell_LT1(bell.Bell):
    mprefix = 'Bell_LT1'

    def __init__(self, name):
        bell.Bell.__init__(self,name)
        for k in params.joint_params:
            self.joint_params[k] = params.joint_params[k]
        for k in params_lt1.params_lt1:
            self.params[k] = params_lt1.params_lt1[k]
        bseq.pulse_defs_lt1(self)

    def autoconfig(self, **kw):
        bell.Bell.autoconfig(self, **kw)
        remote=kw.pop('remote_meas', False)
        if remote_meas:
            remote_params = remote_measurement_helper.get_measurement_params()
            print remote_params
            for k in remote_params:
                self.params[k] = remote_params[k]

    def generate_sequence(self):
        seq = pulsar.Sequence('BellLT3')

        elements = [] 

        dummy_element = bseq._dummy_element(self)
        #finished_element = bseq._sequence_finished_element(self)
        #start_element = bseq._lt3_sequence_start_element(self)
        succes_element = bseq._lt1_entanglement_event_element(self)
        #elements.append(start_element)
        #elements.append(finished_element)
        elements.append(succes_element)
        LDE_element = bseq._LDE_element(self)   
        elements.append(LDE_element)
        
        #seq.append(name = 'start_LDE',
        #    trigger_wait = True,
        #    wfname = start_element.name)

        seq.append(name = 'LDE_LT1',
            wfname = LDE_element.name,
            jump_target = 'RO_dummy',
            goto_target = 'start_LDE',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        #seq.append(name = 'LDE_timeout',
        #    wfname = finished_element.name,
        #    goto_target = 'start_LDE')

        seq.append(name = 'RO_dummy',
            wfname = succes_element.name,
            goto_target = 'start_LDE')
            
        qt.pulsar.program_awg(seq,*elements)

def bell_lt1(name):

    m=Bell_LT1(name)
    
    m.params['MW_during_LDE'] = True
    
    m.autoconfig()
    m.generate_sequence()
    debug=True
    if not debug:
        m.setup(mw=m.params['MW_during_LDE'], pq_calibrate=False)
        m.run(autoconfig=False, setup=False)    
        m.save()
        m.finish()

if __name__ == '__main__':
    bell_lt1('test')
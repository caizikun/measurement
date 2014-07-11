"""
LT3 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import qt
import msvcrt
#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.measurement2.adwin_ssro import ssro
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
        if self.params['remote_measurement']:
            remote_params = self.remote_measurement_helper.get_measurement_params()
            print remote_params
            for k in remote_params:
                self.params[k] = remote_params[k]
        self.remote_measurement_helper.set_data_path(self.h5datapath)

    def measurement_process_running(self):
        if self.params['remote_measurement']:
            return self.remote_measurement_helper.get_is_running()
        else:
            return self.adwin_process_running()

    def print_measurement_progress(self):
        if self.params['remote_measurement']:
            pass
        else:
            bell.Bell.print_measurement_progress(self)

    def generate_sequence(self):
        seq = pulsar.Sequence('BellLT1')

        elements = [] 

        #dummy_element = bseq._dummy_element(self)
        finished_element = bseq._lt1_sequence_finished_element(self)
        start_element = bseq._lt1_sequence_start_element(self)
        succes_element = bseq._lt1_entanglement_event_element(self)
        elements.append(start_element)
        elements.append(finished_element)
        elements.append(succes_element)
        LDE_element = bseq._LDE_element(self, name='LDE_LT1')   
        elements.append(LDE_element)
        
        seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_element.name)

        seq.append(name = 'LDE_LT1',
            wfname = LDE_element.name,
            trigger_wait = False,
            jump_target = 'RO_dummy',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        seq.append(name = 'LDE_timeout',
            wfname = finished_element.name,
            goto_target = 'start_LDE')

        seq.append(name = 'RO_dummy',
            wfname = succes_element.name,
            goto_target = 'start_LDE')
            
        #qt.pulsar.program_awg(seq,*elements)
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(seq)

    #def finish(self):
    #    ssro.IntegratedSSRO.finish(self)

Bell_LT1.remote_measurement_helper = qt.instruments['remote_measurement_helper']

def bell_lt1_local(name):

    upload_only=False
    th_debug=True
    mw = False
    remote_meas = False

    m=Bell_LT1(name) 
    m.params['MW_during_LDE'] = mw
    m.params['remote_measurement'] = remote_meas
    m.autoconfig()
    m.generate_sequence()
    
    if not(upload_only):
        m.setup(debug=th_debug)
        m.run(autoconfig=False, setup=False,debug=th_debug)    
        m.save()
        m.finish()

def bell_lt1_remote(name):

    th_debug=True
    mw = True
    remote_meas = True
    do_upload = True

    m=Bell_LT1(name+'_'+Bell_LT1.remote_measurement_helper.get_measurement_name()) 
    m.params['MW_during_LDE'] = mw
    m.params['remote_measurement'] = remote_meas
    m.autoconfig()

    if do_upload:
        m.generate_sequence()
    
    m.setup(debug=th_debug)
    lt3_ready = False
    while(1):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if m.remote_measurement_helper.get_is_running():
            lt3_ready = True
            qt.msleep(2)
            break
        qt.msleep(1)
    if lt3_ready:
        m.run(autoconfig=False, setup=False,debug=th_debug)    
        m.save()
        m.finish()


if __name__ == '__main__':
    bell_lt1_remote('LT1')
"""
lt4 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import qt
import msvcrt
#reload all parameters and modules
execfile(qt.reload_current_setup)

from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses

import bell
reload(bell)
import sequence as bseq
reload(bseq)
import joint_params
reload(joint_params)
import params_lt3
reload(params_lt3)


class Bell_lt3(bell.Bell):
    mprefix = 'Bell_lt3'
    adwin_process = 'bell_lt3'

    def __init__(self, name):
        bell.Bell.__init__(self,name)
        for k in joint_params.joint_params:
            self.joint_params[k] = joint_params.joint_params[k]
        for k in params_lt3.params_lt3:
            self.params[k] = params_lt3.params_lt3[k]
        bseq.pulse_defs_lt3(self)

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
        seq = pulsar.Sequence('Belllt3')

        elements = [] 

        #dummy_element = bseq._dummy_element(self)
        finished_element = bseq._lt3_sequence_finished_element(self)
        start_element = bseq._lt3_sequence_start_element(self)
        succes_element = bseq._lt3_entanglement_event_element(self)
        elements.append(start_element)
        elements.append(finished_element)
        elements.append(succes_element)
        LDE_element = bseq._LDE_element(self, name='LDE_lt3')   
        elements.append(LDE_element)
        
        #seq.append(name = 'start_LDE',
        #    trigger_wait = True,
        #    wfname = start_element.name)

        seq.append(name = 'LDE_lt3',
            wfname = LDE_element.name,
            trigger_wait = True,
            jump_target = 'RO_dummy',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        seq.append(name = 'LDE_timeout',
            wfname = finished_element.name,
            goto_target = 'LDE_lt3')

        seq.append(name = 'RO_dummy',
            wfname = succes_element.name,
            goto_target = 'LDE_lt3')
            
        #qt.pulsar.program_awg(seq,*elements)
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(seq)


Bell_lt3.remote_measurement_helper = qt.instruments['remote_measurement_helper']
Bell_lt3.AWG_RO_AOM = qt.instruments['PulseAOM']#Bell_lt3.E_aom


def bell_lt3_local(name):

    upload_only=False
    th_debug=True
    mw = False
    remote_meas = False

    m=Bell_lt3(name) 
    m.params['MW_during_LDE'] = mw
    m.params['remote_measurement'] = remote_meas
    m.autoconfig()
    m.generate_sequence()
    
    if not(upload_only):
        m.setup(debug=th_debug)
        m.run(autoconfig=False, setup=False,debug=th_debug)    
        m.save()
        m.finish()

def bell_lt3_remote(name):

    th_debug=True
    mw = False
    remote_meas = True
    do_upload = True
    remote_name=Bell_lt3.remote_measurement_helper.get_measurement_name()
    m=Bell_lt3(name+'_'+remote_name) 
    m.params['MW_during_LDE'] = mw
    m.params['remote_measurement'] = remote_meas
    if 'XXSPCORRXX' in remote_name:
        m.joint_params['RO_during_LDE']=0
        m.joint_params['do_echo'] = 0
        m.joint_params['do_final_MW_rotation'] = 0
    m.autoconfig()

    if do_upload:
        m.generate_sequence()
    
    m.setup(debug=th_debug)
    lt4_ready = False
    while(1):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break
        if m.remote_measurement_helper.get_is_running():
            lt4_ready = True
            qt.msleep(2)
            break
        qt.msleep(1)
    if lt4_ready:
        m.run(autoconfig=False, setup=False,debug=th_debug)    
        m.save()
        m.finish()


if __name__ == '__main__':
    bell_lt3_remote('')
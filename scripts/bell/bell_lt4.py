"""
lt4 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import inspect
import qt
import time
from measurement.scripts.bell import check_awg_triggering as JitterChecker
reload(JitterChecker)
#reload all parameters and modules
execfile(qt.reload_current_setup)
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
from measurement.lib.config import moss as moscfg

import bell
reload(bell)
import sequence as bseq
reload(bseq)
import joint_params
reload(joint_params)
import params_lt4
reload(params_lt4)

class Bell_lt4(bell.Bell):
    mprefix = 'Bell_lt4'
    adwin_process = 'bell_lt4'

    def __init__(self, name):
        bell.Bell.__init__(self,name)
        for k in joint_params.joint_params:
            self.joint_params[k] = joint_params.joint_params[k]
        for k in params_lt4.params_lt4:
            self.params[k] = params_lt4.params_lt4[k]
        bseq.pulse_defs_lt4(self)


    def generate_sequence(self):
        seq = pulsar.Sequence('Belllt4')

        elements = [] 

        dummy_element = bseq._dummy_element(self)
        succes_element = bseq._lt4_entanglement_event_element(self)
        elements.append(succes_element)
        #finished_element = bseq._sequence_finished_element(self)
        start_element = bseq._lt4_sequence_start_element(self)
        elements.append(start_element)
        #elements.append(finished_element)
        elements.append(dummy_element)
        LDE_element = bseq._LDE_element(self, name='LDE_lt4')   
        elements.append(LDE_element)

        if self.joint_params['wait_for_1st_revival']:
            LDE_echo_point = LDE_element.length()- (LDE_element.pulses['MW_pi'].effective_start()+ self.params['MW_1_separation'])
            late_RO = bseq._1st_revival_RO(self, LDE_echo_point = LDE_echo_point, name = '1st_revival_RO_lt4')
            elements.append(late_RO)
        elif self.joint_params['TPQI_normalisation_measurement']:
            self.params['opt_pulse_start'] = self.params['opt_pulse_start'] + 300e-9
            TPQI_normalisation_element = bseq._LDE_element(self, name='LDE_lt4_TPQI_norm')
            self.params['opt_pulse_start'] = self.params['opt_pulse_start'] - 300e-9
            elements.append(TPQI_normalisation_element)


        seq.append(name = 'start_LDE',
            trigger_wait = True,
            wfname = start_element.name)

        seq.append(name = 'LDE_lt4',
            wfname = LDE_element.name,
            jump_target = 'late_RO' if self.joint_params['wait_for_1st_revival'] else 'RO_dummy',
            goto_target = 'start_LDE_2' if self.joint_params['TPQI_normalisation_measurement'] else 'start_LDE',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        #seq.append(name = 'LDE_timeout',
        #    wfname = finished_element.name,
        #    goto_target = 'start_LDE')
        if self.joint_params['wait_for_1st_revival']:
            seq.append(name = 'late_RO',
                wfname = late_RO.name,
                goto_target = 'start_LDE')
        elif self.joint_params['TPQI_normalisation_measurement']:
            seq.append(name = 'start_LDE_2',
            trigger_wait = True,
            wfname = start_element.name)
            seq.append(name = 'LDE_lt4_TPQI_norm',
            wfname = TPQI_normalisation_element.name,
            jump_target = 'RO_dummy',
            goto_target = 'start_LDE',
            repetitions = self.joint_params['LDE_attempts_before_CR'])

        seq.append(name = 'RO_dummy',
            wfname = succes_element.name,
            goto_target = 'start_LDE')
            
        #qt.pulsar.program_awg(seq,*elements)
        qt.pulsar.upload(*elements) 
        qt.pulsar.program_sequence(seq)

    def stop_measurement_process(self):
        bell.Bell.stop_measurement_process(self)

        # signal BS and lt3 to stop as well
        if self.bs_helper != None:
            self.bs_helper.set_is_running(False)
        if self.lt3_helper != None:    
            self.lt3_helper.set_is_running(False)

    def print_measurement_progress(self):
        pass

    def finish(self):
        bell.Bell.finish(self)
        self.add_file(inspect.getsourcefile(bseq))

Bell_lt4.bs_helper = qt.instruments['bs_helper']
Bell_lt4.lt3_helper = qt.instruments['lt3_helper']
Bell_lt4.mos = qt.instruments['master_of_space']
Bell_lt4.AWG_RO_AOM = qt.instruments['PulseAOM']

def bell_lt4(name, 
             m,
             th_debug,
             sequence_only,
             mw,
             measure_lt3,
             measure_bs,
             do_upload,
             ):

    m.params['MW_during_LDE'] = mw
    m.params['wait_for_remote_CR'] = measure_lt3


    if not(sequence_only):
        if measure_lt3:
            m.lt3_helper.set_is_running(False)
            qt.msleep(0.5)
            m.lt3_helper.set_measurement_name(name)
            m.lt3_helper.set_script_path(r'Y:/measurement/scripts/bell/bell_lt3.py')
            m.lt3_helper.execute_script()
        if measure_bs:
            m.bs_helper.set_is_running(False)
            qt.msleep(0.5)
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
    #m.reset_plu()
    
    print '='*10
    print name
    print 'Measreument started: ', time.strftime('%H:%M')
    print '='*10

    if measure_lt3: 
        m.lt3_helper.set_is_running(True)
        qt.msleep(2)
    m.run(autoconfig=False, setup=False,debug=th_debug,live_filter_on_marker=m.joint_params['use_live_marker_filter'])
    m.save()

    if measure_lt3:
        m.params['lt3_data_path'] = m.lt3_helper.get_data_path()
        m.lt3_helper.set_is_running(False)
    if measure_bs:
        m.bs_helper.set_is_running(False)
        m.params['bs_data_path'] = m.bs_helper.get_data_path()  
    
    print 'finishing'
    m.finish()
    print 'finished'



def full_bell(name):
    name='full_Bell'+name
    m = Bell_lt4(name) 
    bell_lt4(name, 
             m,
             th_debug      = False,
             sequence_only = False,
             mw            = True,
             measure_lt3   = True,
             measure_bs    = True,
             do_upload     = True,
             )

def measureXX(name):
    name='MeasXX_'+name
    m = Bell_lt4(name)
    #make sure MWI and Q pulses are set correctly
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = True,
             measure_lt3   = True,
             measure_bs    = True,
             do_upload     = True,
             )

def pulse_overlap(name):
    m = Bell_lt4(name) 
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = False,
             measure_lt3   = True,
             measure_bs    = False,
             do_upload     = True,
             )

def TPQI(name):
    name= 'TPQI_'+name
    m = Bell_lt4(name)
    m.joint_params['RO_during_LDE']=0
    m.joint_params['do_echo'] = 0
    m.joint_params['do_final_MW_rotation'] = 0
    m.joint_params['RND_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 15
    m.joint_params['TPQI_normalisation_measurement'] = True
    m.joint_params['LDE_element_length'] = 10.e-6+(m.joint_params['opt_pi_pulses']-2)*m.joint_params['opt_pulse_separation']
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = False,
             measure_lt3   = True,
             measure_bs    = True,
             do_upload     = True,
             )

def SP_lt4(name): #we now need to do the RO in the AWG, because the PLU cannot tell the adwin to do ssro anymore.
    name='SPCORR_'+name
    m = Bell_lt4(name)
    m.joint_params['do_echo'] = 0
    m.joint_params['do_final_MW_rotation'] = 0
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = True,
             measure_lt3   = True,
             measure_bs    = True,
             do_upload     = True,
             )

def SP_lt3(name):
    name='SPCORR_'+name
    m = Bell_lt4(name)
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = False,
             measure_lt3   = True,
             measure_bs    = True,
             do_upload     = True,
             )

def lt4_only(name):
    m = Bell_lt4(name)
    bell_lt4(name, 
             m,
             th_debug      = True,
             sequence_only = False,
             mw            = True,
             measure_lt3   = False,
             measure_bs    = False,
             do_upload     = True,
             )

if __name__ == '__main__':
    DoJitterCheck = True
    ResetPlu = True
        
    if ResetPlu:
        stools.reset_plu()

    if DoJitterCheck:
        jitterDetected = JitterChecker.do_jitter_test(resetAWG=False)
        print 'Here comes the result of the jitter test: jitter detected = '+ str(jitterDetected)
    else: 
        jitterDetected = False
        print 'I will skip the jitter test.'
    

    if not(jitterDetected):
        qt.msleep(0.5)
        #TPQI('run_test')
        #full_bell('high_strain_short_pulsesep_day1_run2')   
        #SP_lt4('SPCORR_lt4')
        #lt4_only('test')
        #pulse_overlap('testing')
        #SP_lt3('SPCORR_lt3')
        measureXX('high_strain_short_pulsesep_day2_run16')
        passex
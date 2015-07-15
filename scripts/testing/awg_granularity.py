import os
import qt
import numpy as np
import msvcrt

#from measurement.lib.AWG_HW_sequencer_v2 import Sequence
#from measurement.lib.config import awgchannels as awgcfg
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import pprint

reload(pulse)
reload(element)
reload(pulsar)
#reload(awgcfg)

pulsar.Pulsar.AWG = qt.instruments['AWG']
#AWG = qt.instruments['AWG']

'''
def generate_sequence_old (do_program=True):
        seq = Sequence('Test')

        # vars for the channel names
        gate_chan= 'gate'
        clock_chan='clock'
        
        
        awgcfg.configure_sequence(seq, 'mw','awg_FPGA_test')
        
        ename='trigger'
        seq.add_element(ename,goto_target='trigger')
        #start_reference='before',link_start_to='end',
        #seq.add_pulse('before',trigger_chan,ename,start=0,duration=1000,amplitude=0)
        seq.add_pulse('gate',gate_chan,ename,start=100,duration=500, amplitude=1.0)
        seq.add_pulse('first_clock',clock_chan,ename,start=0,duration=3, amplitude=0)
        last='first_clock'
        for i in arange(1000):
            seq.add_pulse('clock_up %d'%i,clock_chan,ename,start=0,
                start_reference=last, link_start_to = 'end',duration=12, amplitude=1.0)
            last='clock_up %d'%i
            seq.add_pulse('clock_down %d'%i,clock_chan,ename,start=0,
                start_reference=last, link_start_to = 'end',duration=12, amplitude=0)        
            last='clock_down %d'%i
         #sweep the pulse length
       
        seq.set_instrument(AWG)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True
'''
def generate_sequence (do_program = True):

    # FIXME in principle we only want to create that once, at startup
    try:
        del qt.pulsar 
    except:
        pass
    qt.pulsar = pulsar.Pulsar()
    qt.pulsar.AWG_sequence_cfg={
        'SAMPLING_RATE'             :   1e9,
        'CLOCK_SOURCE'              :   1,    # Internal | External
        'REFERENCE_SOURCE'          :   2,    # Internal | External
        'EXTERNAL_REFERENCE_TYPE'   :   1,    # Fixed | Variable
        'REFERENCE_CLOCK_FREQUENCY_SELECTION':1, #10 MHz | 20 MHz | 100 MHz
        'TRIGGER_SOURCE'            :   1,    # External | Internal
        'TRIGGER_INPUT_IMPEDANCE'   :   1,    # 50 ohm | 1 kohm
        'TRIGGER_INPUT_SLOPE'       :   1,    # Positive | Negative
        'TRIGGER_INPUT_POLARITY'    :   1,    # Positive | Negative
        'TRIGGER_INPUT_THRESHOLD'   :   1.4,  # V
        'EVENT_INPUT_IMPEDANCE'     :   2,    # 50 ohm | 1 kohm
        'EVENT_INPUT_POLARITY'      :   1,    # Positive | Negative
        'EVENT_INPUT_THRESHOLD'     :   1.4,  #V
        'JUMP_TIMING'               :   1,    # Sync | Async
        'RUN_MODE'                  :   4,    # Continuous | Triggered | Gated | Sequence
        'RUN_STATE'                 :   0,    # On | Off
        }

    qt.pulsar.define_channel(id='ch2', name='gate', type='analog', 
        high=4.0, low=0, offset=0., delay=0., active=True)
    qt.pulsar.define_channel(id='ch4', name='clock', type='analog', 
        high=4.0, low=0, offset=0., delay=0., active=True)
    

    pulse_length = 2e-9

    gate = pulse.SquarePulse(channel = 'gate')
    clock_up = pulse.SquarePulse(channel = 'clock', amplitude = 4.0, lenght = 970e-9)
    clock_down = pulse.SquarePulse(channel = 'clock', amplitude = 0, lenght = 970e-9)
 
    elt1 = element.Element('trigger', pulsar = qt.pulsar)
    elt1.append(pulse.cp(clock_down, amplitude = 0.5, length =249e-9))
    
    
   
    '''
    for i in arange (500):
        elt1.append(pulse.cp(clock_up, amplitude = 4.0, length = pulse_length))
        elt1.append(pulse.cp(clock_down, amplitude = 0, length = pulse_length))
    elt1.append(pulse.cp(clock_down, amplitude = 0, length = 1000e-9))
    elt1.add(pulse.cp(gate, amplitude = 4.0, length = 100*pulse_length))    
    for i in arange (2):
        elt1.append(pulse.cp(clock_up, amplitude = 4.0, length = pulse_length))
        elt1.append(pulse.cp(clock_down, amplitude = 0, length = pulse_length))
    #pprint.pprint (elt1.pulses)
    '''
    seq = pulsar.Sequence('FPGA_test')
    seq.append(name = 'trigger2', wfname = elt1.name, trigger_wait = False, repetitions = 1)

    seq.append(name = 'trigger', wfname = elt1.name, trigger_wait = False, repetitions = 1, jump_target='trigger2', goto_target = 'trigger')
    #pprint.pprint (seq.elements)

    qt.pulsar.upload(elt1)
    qt.pulsar.program_sequence(seq)


if __name__ == "__main__":
    generate_sequence()

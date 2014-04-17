import os
import qt
import numpy as np
import msvcrt

from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels as awgcfg

reload(awgcfg)

 

AWG = qt.instruments['AWG']

def generate_sequence(do_program=True):
        seq = Sequence('Test')

        # vars for the channel names
        gate_chan= 'gate'
        clock_chan='clock'
        
        
        awgcfg.configure_sequence(seq, 'mw','awg_FPGA_test')
        
        ename='trigger'
        seq.add_element(ename,goto_target='trigger')
        #start_reference='before',link_start_to='end',
        #seq.add_pulse('before',trigger_chan,ename,start=0,duration=1000,amplitude=0)
        seq.add_pulse('gate',gate_chan,ename,start=100,duration=500, amplitude=3.5)
        seq.add_pulse('first_clock',clock_chan,ename,start=0,duration=3, amplitude=0)
        last='first_clock'
        for i in arange(1000):
            seq.add_pulse('clock_up %d'%i,clock_chan,ename,start=0,
                start_reference=last, link_start_to = 'end',duration=12, amplitude=3.5)
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

    
if __name__ == "__main__":

    generate_sequence()

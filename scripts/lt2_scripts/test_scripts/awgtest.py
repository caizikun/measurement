import qt
import measurement.lib.measurement2.measurement as m2
from measurement.lib.config import awgchannels_lt2 as awgcfg
#from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


reload(awgcfg)
try:
    del qt.pulsar
except:
    pass
qt.pulsar = pulsar.Pulsar()
#os.chdir('D:/measuring/qtlab/')
#reload(awgcfg)
#os.chdir('D:/measuring/user/scripts/lt2_scripts/')

#awgcfg.configure_sequence(seq,'mw')

#seq.add_channel('PH_start', 'ch4m2', cable_delay=0)
#seq.add_channel('Green', 'ch2m1', cable_delay=604, high=0.5)
#seq.add_channel('MW_pulsemod', 'ch2m2', high=2.0, cable_delay = 0)
#seq.add_channel('MW_Imod', 'ch1', high=0.9, low=-0.9)
#seq.add_channel('MW_Qmod', 'ch4', high=0.9, low=-0.9, cable_delay = 0)
#qt.pulsar.define_channel(id='ch2_marker2', name='trigger', type='marker',
#            high=2.0, low=0, offset=0., delay=0., active=True)
#seq.add_channel('pm','ch1m1', high=2.0, cable_delay=27)
awgcfg.config['JUMP_TIMING']=1
awgcfg.config['CLOCK']=1e9

trigger = 'trigger'
chan_mw_pm = 'MW_pulsemod'
chan_mwI = 'MW_Qmod'
chan_mwQ = 'MW_Imod'

MW_pulse_mod_risetime = 10#10#6 = correct for LT2, 2 =  correct for LT1
MW_Imod_duration = 40



#seq.add_pulse('PH', 'PH_start', elt, start=0, duration=50)

#seq.add_pulse('Green', 'Green', elt, start=0, amplitude = 1, duration=5000,start_reference = 'PH',link_start_to='end')
#seq.add_pulse('Wait', 'Green', elt, start=0, amplitude=1,duration=750,start_reference = 'Green',link_start_to='end')

#seq.add_IQmod_pulse(name='mwburst', channel=('MW_Imod','MW_Qmod'),
#                    element=elt, start = 2000, duration = 1500,
#                    start_reference = 'Green',
#                    link_start_to = 'start', frequency=0)

#seq.clone_channel('MW_pulsemod', 'MW_Imod', elt,
#                start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime,
#                link_start_to = 'start', link_duration_to = 'duration',
#                amplitude = 2.0)
qt.pulsar.define_channel(id='ch2_marker2', name='trigger', type='marker',
    high=1.0, low=0, offset=0., delay=0e-9, active=True)
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker',
    high=2.0, low=0, offset=0., delay=0e-9, active=True)
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=0e-9, active=True)
#qt.pulsar.define_channel(id='ch2', name='MW_Qmod', type='analog', high=0.9,
#    low=-0.9, offset=0., delay=240e-9, active=True)

trigger = pulse.SquarePulse(channel = 'trigger',name='tr', amplitude = 1.0)
MWI = pulse.SquarePulse(channel = 'MW_Imod',name='MW_pulse', amplitude = 1.0)
wait = pulse.SquarePulse(channel = 'MW_Imod',name='wait', amplitude = 1.0)
MW_pulm = pulse.SquarePulse(channel = 'MW_pulsemod', amplitude = 1.0)

elt = 'test'
elt1 = element.Element('idle', pulsar = qt.pulsar)

elt1.add(pulse.cp(wait, amplitude = 0.0, length = 700e-9), start = 0e-9)
elt1.add(pulse.cp(trigger, amplitude = 1.0, length = 10e-9), start = 675e-9)
elt1.add(pulse.cp(MWI, amplitude = 1.0, length = 50e-9), start = 700e-9)
elt1.add(pulse.cp(MW_pulm, amplitude = 1.0, length = 100e-9), start = 675e-9)
elt1.add(pulse.cp(wait, amplitude = 0.0, length = 250e-9), start = 750e-9)

"""
seq.add_pulse(name='trigger', channel = trigger, element=elt,
        start = 0, duration = 50 )
seq.add_pulse(name='trigger_empty', channel = trigger, element=elt,
        start = 0, duration = 1000, amplitude = 0 )
seq.add_pulse(name='wait', channel = chan_mwI, element=elt,
        start=0, duration = 500, amplitude = 0)

seq.add_pulse(name='MW_Imod_base', channel = chan_mwI,element = elt, duration = MW_Imod_duration*2,
        start_reference='wait',link_start_to = 'end', amplitude = 0.5)
seq.add_pulse(name='MW_Imod', channel = chan_mwI, element = elt, duration = MW_Imod_duration,
        start_reference='MW_Imod_base', link_start_to = 'start', amplitude = 0.5, start=MW_Imod_duration/2)

seq.add_pulse(name='wait2', channel = chan_mwI, element=elt,
        start_reference='MW_Imod',link_start_to='end', duration = 500-MW_Imod_duration-23, amplitude = 0)


seq.add_pulse(name = 'MW_Pmod', channel = chan_mw_pm, element = elt,
            start=-MW_pulse_mod_risetime, duration=2*MW_pulse_mod_risetime,
            start_reference = 'MW_Imod', link_start_to = 'start', duration_reference = 'MW_Imod', link_duration_to = 'duration')

print 'MW pulse mod duration = ',(2*MW_pulse_mod_risetime+MW_Imod_duration)
"""
##seq.add_pulse(name='MWpulse', channel = 'pm', element=elt,
##        start_reference='wait',link_start_to='end', duration = 100)
seq = pulsar.Sequence('AWG Test')
seq.append(name = 'idle', wfname = elt1.name, trigger_wait = False, repetitions = 1, goto_target = 'idle')


SMB100.set_status('off')
SMB100.set_power(0)
SMB100.set_frequency(1e9)
SMB100.set_iq('on')
SMB100.set_pulm('on')
SMB100.set_status('on')


#qt.pulsar.upload(elt1)
#qt.pulsar.program_sequence(seq)
qt.pulsar.program_awg(seq,elt1)
AWG.set_clock(1e9)
#seq.set_instrument(AWG)
#seq.set_clock(1e9)
#seq.set_send_waveforms(True)
#seq.set_send_sequence(True)
#seq.set_program_channels(True)
#seq.set_start_sequence(True)
#seq.force_HW_sequencing(True)
#seq.send_sequence()



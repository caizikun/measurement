import qt

from measurement.lib.pulsar import pulsar
reload(pulsar)

pulsar.Pulsar.AWG = qt.instruments['AWG']

# FIXME in principle we only want to create that once, at startup
try:
    del qt.pulsar 
except:
    pass
qt.pulsar = pulsar.Pulsar()
qt.pulsar.AWG_type = 'opt09'
qt.pulsar.clock = 1e9


# analog channels
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=1.0, #name = 'MW_1'
    low=-1.0, offset=0., delay=200e-9, active=True) #DD
qt.pulsar.define_channel(id='ch2', name='MW_Qmod', type='analog', high=1.0,  #name = 'MW_2'
    low=-1.0, offset=0., delay=200e-9, active=True) #DD # note measured delay on fast scope 2014-10-13: 59 ns
qt.pulsar.define_channel(id='ch3', name='EOM_AOM_Matisse', type='analog', 
    high=1.0, low=-1.0, offset=0.0, delay=(490e-9+ 5e-9), active=True) #DD #617 ns for normal pulses 458e-9
qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=2.0,
    low=-2.0, offset=0., delay=(199e-9+100e-9-20e-9), active=True) #DD #measured delay on apd's (tail) 2014-10-13: 40 ns


# marker channels
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=268e-9, active=True) ##267e-9#DD #previous 267e-9# previous:289; measured 242e-9 on the scope made an error??2014-10-13
qt.pulsar.define_channel(id='ch1_marker2', name='sync', type='marker', # HydraHarp Sync
    high=2.0, low=0, offset=0., delay=102e-9, active=True) #XX plug in/ calibrate delay

qt.pulsar.define_channel(id='ch2_marker1', name='plu_sync', type='marker', 
   high=2.0, low=0, offset=0, delay=182e-9, active=True)

qt.pulsar.define_channel(id='ch3_marker1', name='adwin_sync', type='marker', 
    high=2.0, low=0.0, offset=0., delay=0., active=True) 
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_count', type='marker', 
    high=2.0, low=0, offset=0., delay=0e-9, active=True)

qt.pulsar.define_channel(id='ch4_marker1', name='AOM_Newfocus', type='marker',
    high=0.4, low=0.0, offset=0.0, delay=200e-9, active=True) #DD

# define optical voltages
qt.pulsar.set_channel_opt('EOM_AOM_Matisse','offset', qt.instruments['PulseAOM'].get_sec_V_off())
qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Newfocus','low',  qt.instruments['NewfocusAOM'].get_sec_V_off())

qt.pulsar.AWG_sequence_cfg={
        'SAMPLING_RATE'             :   qt.pulsar.clock,
        'TRIGGER_SOURCE'            :   1,    # External | Internal
        'TRIGGER_INPUT_IMPEDANCE'   :   1,    # 50 ohm | 1 kohm
        'TRIGGER_INPUT_SLOPE'       :   1,    # Positive | Negative
        'TRIGGER_INPUT_POLARITY'    :   1,    # Positive | Negative
        'TRIGGER_INPUT_THRESHOLD'   :   1.0,  # V
        'EVENT_INPUT_IMPEDANCE'     :   1,    # 50 ohm | 1 kohm
        'EVENT_INPUT_POLARITY'      :   1,    # Positive | Negative
        'EVENT_INPUT_THRESHOLD'     :   0.8,  #V
        'JUMP_TIMING'               :   1,    # Sync | Async
        'RUN_MODE'                  :   4,    # Continuous | Triggered | Gated | Sequence
        'RUN_STATE'                 :   0,    # On | Off
}
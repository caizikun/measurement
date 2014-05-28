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

### channels
# RF
#RF channel is needed for the AOM for the short pulses
#qt.pulsar.define_channel(id='ch1', name='RF', type='analog', high=1.5,
#    low=-1.5, offset=0., delay=165e-9, active=True)

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=(44+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch4', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)

# sync ADwin
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# light
qt.pulsar.define_channel(id='ch2_marker2', name='AOM_Newfocus', type='marker', 
    high=0.4, low=0, offset=0., delay=700e-9, active=True)

qt.pulsar.define_channel(id='ch1_marker2', name='AOM_Yellow', type='marker', 
    high=0.4, low=0, offset=0., delay=750e-9, active=True)

## EOM - short pulse
qt.pulsar.define_channel(id='ch2', name='EOM_Matisse', type='analog', high=1.5,
    low=-1.5, offset=0., delay=112e-9, active=True)

qt.pulsar.define_channel(id='ch1', name='EOM_AOM_Matisse', type='analog',
    high=1.0, low=-1.0, offset=0., delay=416e-9, active=True)

#PLU
qt.pulsar.define_channel(id='ch2_marker1', name='plu_sync', type='marker',
    high=2.0, low=0, offset=0., delay=14e-9, active=True)


#RND
qt.pulsar.define_channel(id='ch4_marker1', name='RND_halt', type='marker', 
    high=2.0, low=0, offset=0., delay=0e-9, active=True)

qt.pulsar.define_channel(id='ch4_marker2', name='sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)   


#qt.pulsar.define_channel(id='ch2', name='AOM_Newfocus', type='analog', 
#    high=0.4, low=0, offset=0., delay=700e-9, active=True)
#qt.pulsar.define_channel(id='ch2_marker2', name='YellowAOM', type='marker', 
#    high=0.4, low=0, offset=0., delay=750e-9, active=True)

# Trigger AWG LT2
qt.pulsar.define_channel(id='ch3_marker1', name='scope_pulse', type='marker', 
    high=0.5, low=0, offset=0., delay=0., active=True)

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

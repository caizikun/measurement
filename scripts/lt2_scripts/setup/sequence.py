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
### channels
# RF
# qt.pulsar.define_channel(id='ch2', name='RF', type='analog', high=1.0,
#     low=-1.0, offset=0., delay=242e-9, active=True)

spin_of = -104e-9-27e-9

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker',
    high=2.0, low=0, offset=0., delay=spin_of+260e-9, active=True)
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+240e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+240e-9, active=True)

#RF
qt.pulsar.define_channel(id='ch4', name='RF', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+240e-9, active=True)

# sync ADwin
qt.pulsar.define_channel(id='ch1_marker2', name='adwin_sync', type='marker',
    high=2.0, low=0, offset=0., delay=0., active=True)

# #HH
# qt.pulsar.define_channel(id='ch2_marker2', name='HH_sync', type='marker',
#     high=2.0, low=0, offset=0., delay=0., active=True)
# qt.pulsar.define_channel(id='ch3_marker1', name='HH_MA1', type='marker',
#     high=2.0, low=0, offset=0., delay=0., active=True)

#EOM
#qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=1.5,
#    low=-1.5, offset=0., delay=112e-9, active=True)


qt.pulsar.define_channel(id='ch2', name='fpga_gate', type='analog', 
        high=4.0, low=0, offset=0., delay=148e-9, active=True)
qt.pulsar.define_channel(id='ch4_marker1', name='fpga_clock', type='marker', 
        high=1.0, low=0, offset=0., delay=0., active=True)
 

'''
# 2013-12-03: trying different channel def. to make a shorter eom pulse
qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=2.8,
    low=-1.25, offset=0., delay=112e-9, active=True)

qt.pulsar.define_channel(id='ch3_marker2', name='EOM_trigger', type='marker',
     high=2.0, low=0.0, offset=0., delay=0e-9, active=True)
'''

#AOMs
#qt.pulsar.define_channel(id='ch4_marker1', name='EOM_AOM_Matisse', type='marker',
#    high=1.0, low=0.02, offset=0., delay=416e-9, active=True)

qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
    high=0.4, low=0.0, offset=0., delay=466e-9, active=True)
qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Newfocus','low',  qt.instruments['NewfocusAOM'].get_sec_V_off())

qt.pulsar.define_channel(id='ch2_marker2', name='AOM_Matisse', type='marker',
    high=0.4, low=0.0, offset=0., delay=466e-9, active=True)
qt.pulsar.set_channel_opt('AOM_Matisse','high', qt.instruments['MatisseAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Matisse','low',  qt.instruments['MatisseAOM'].get_sec_V_off())

#qt.pulsar.define_channel(id='ch3_marker2', name='AOM_Yellow', type='marker',
#     high=0.4, low=0.0, offset=0., delay=466e-9, active=True)
#qt.pulsar.set_channel_opt('AOM_Yellow','high', qt.instruments['YellowAOM'].get_sec_V_max())
#qt.pulsar.set_channel_opt('AOM_Yellow','low', qt.instruments['YellowAOM'].get_sec_V_off())

#PLU
#qt.pulsar.define_channel(id='ch4_marker2', name='plu_sync', type='marker',
#    high=2.0, low=0, offset=0., delay=14e-9, active=True)

### TMP HH debug channel -- normally there's RF on this output.
#qt.pulsar.define_channel(id='ch2', name='HH_test', type='analog', high=2.0,
#    low=0, offset=0., delay=0, active=True)

qt.pulsar.AWG_sequence_cfg={
        'SAMPLING_RATE'             :   qt.pulsar.clock,
        'TRIGGER_SOURCE'            :   1,    # External | Internal
        'TRIGGER_INPUT_IMPEDANCE'   :   2,    # 50 ohm | 1 kohm
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

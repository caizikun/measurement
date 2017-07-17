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
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=1.0,
    low=-1.0, offset=0.00195, delay=230e-9, active=True)  #230e-9
qt.pulsar.define_channel(id='ch2', name='MW_Qmod', type='analog', high=1.0,
    low=-1.0, offset=0.0028, delay=230e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='EOM_AOM_Matisse', type='analog', 
    high=1.0, low=-1.0, offset=0.0, delay=464e-9+17e-9, active=True) #546e-9 # PH Note that shifted from + 17e-9 to buy power
qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=2.0,
    low=-2.0, offset=0., delay=200e-9, active=True)


# Marker channels
# qt.pulsar.define_channel(id='ch1_marker1', name='sync', type='marker', # TH sync
#     high=2.0, low=0, offset=0., delay=0., active=True)   

qt.pulsar.define_channel(id='ch1_marker1', name='AOM_Yellow', type='marker', 
    high=0.6, low=0, offset=0., delay=0., active=True)   
qt.pulsar.define_channel(id='ch1_marker2', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=269e-9-16e-9, active=True) #269 or SGS100. was a delay of 302 for SMB100

qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
    high=0.4, low=0.0, offset=0.0, delay=230e-9, active=True) # do not change delay! ASK NK before changing!
qt.pulsar.define_channel(id='ch2_marker2', name='mw_switch', type='marker',
    high = 2.0, low=0.0, offset=0.0, delay=230e-9, active=True)


qt.pulsar.define_channel(id='ch3_marker1', name='adwin_count', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

qt.pulsar.define_channel(id='ch4_marker1', name='HHsync', type='marker',  #Purification: one awg needs to sync all time tagging devices.
   high=2.0, low=0, offset=0., delay=0., active=True)
# qt.pulsar.define_channel(id='ch4_marker2', name='plu_sync', type='marker',  #Purification: Plu synced by other setup
#    high=2.0, low=0, offset=0., delay=102e-9-21e-9-1e-9, active=True)
qt.pulsar.define_channel(id='ch4_marker2', name='tico_sync', type='marker',
    high=2.0, low=0, offset=0., delay=0., active=True)


# define optical voltages
qt.pulsar.set_channel_opt('EOM_AOM_Matisse','offset', qt.instruments['PulseAOM'].get_sec_V_off())
# qt.pulsar.set_channel_opt('EOM_AOM_Matisse','offset', 0.5)
qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Newfocus','low',  qt.instruments['NewfocusAOM'].get_sec_V_off())
# qt.pulsar.set_channel_opt('AOM_Newfocus','low',  0.1)
qt.pulsar.set_channel_opt('AOM_Yellow','high', qt.instruments['YellowAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Yellow','low',  qt.instruments['YellowAOM'].get_sec_V_off())

qt.pulsar.AWG_sequence_cfg={
        'SAMPLING_RATE'             :   qt.pulsar.clock,
        'TRIGGER_SOURCE'            :   1,    # External | Internal
        'CLOCK_SOURCE'              :   1,    # Internal | External
        'REFERENCE_SOURCE'          :   1,    # Internal | External
        'EXTERNAL_REFERENCE_TYPE'   :   1,    # Fixed | Variable
        'REFERENCE_CLOCK_FREQUENCY_SELECTION':1, #10 MHz | 20 MHz | 100 MHz
        'TRIGGER_INPUT_IMPEDANCE'   :   1,    # 50 ohm | 1 kohm
        'TRIGGER_INPUT_SLOPE'       :   1,    # Positive | Negative
        'TRIGGER_INPUT_POLARITY'    :   1,    # Positive | Negative
        'TRIGGER_INPUT_THRESHOLD'   :   1.0,  # V
        'EVENT_INPUT_IMPEDANCE'     :   1,    # 50 ohm | 1 kohm
        'EVENT_INPUT_POLARITY'      :   1,    # Positive | Negative
        'EVENT_INPUT_THRESHOLD'     :   1.0,  #V
        'JUMP_TIMING'               :   1,    # Sync | Async
        'RUN_MODE'                  :   4,    # Continuous | Triggered | Gated | Sequence
        'RUN_STATE'                 :   0,    # On | Off
}
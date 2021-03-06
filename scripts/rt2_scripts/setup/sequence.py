"""
sequence script taken and altered from lt1 on the 18-09-2014

Norbert Kalb
"""

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
    high=2.0, low=0, offset=0., delay=(44+165-8)*1e-9, active=True)
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch2', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)


qt.pulsar.define_channel(id='ch1_marker2', name='katana_trg', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
# p7889 start trigger
qt.pulsar.define_channel(id='ch4_marker1', name='p7889_start', type='marker', 
    high=1.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch3_marker1', name='sync0', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
qt.pulsar.define_channel(id='ch3_marker2', name='sync1', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# light (green)
qt.pulsar.define_channel(id='ch2_marker2', name='AOM_Green', type='marker', 
    high=0.3, low=0., offset=0., delay=2.5e-6, active=True)


qt.pulsar.AWG_sequence_cfg={
        'SAMPLING_RATE'             :   1e9,
        'CLOCK_SOURCE'              :   1,    # Internal | External
        'REFERENCE_SOURCE'          :   1,    # Internal | External
        'EXTERNAL_REFERENCE_TYPE'   :   1,    # Fixed | Variable
        'REFERENCE_CLOCK_FREQUENCY_SELECTION':1, #10 MHz | 20 MHz | 100 MHz
        'TRIGGER_SOURCE'            :   1,    # External | Internal
        'TRIGGER_INPUT_IMPEDANCE'   :   2,    # 50 ohm | 1 kohm
        'TRIGGER_INPUT_SLOPE'       :   1,    # Positive | Negative
        'TRIGGER_INPUT_POLARITY'    :   1,    # Positive | Negative
        'TRIGGER_INPUT_THRESHOLD'   :   0.6,  # V
        'EVENT_INPUT_IMPEDANCE'     :   2,    # 50 ohm | 1 kohm
        'EVENT_INPUT_POLARITY'      :   1,    # Positive | Negative
        'EVENT_INPUT_THRESHOLD'     :   1.4,  #V
        'JUMP_TIMING'               :   1,    # Sync | Async
        'RUN_MODE'                  :   4,    # Continuous | Triggered | Gated | Sequence
        'RUN_STATE'                 :   0,    # On | Off
}

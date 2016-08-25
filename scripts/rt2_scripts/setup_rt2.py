"""
content copied and altered from lt1_scripts setup_lt1.py

so far only the sequence.py file is implemented.

Norbert 18-09-2014
"""

import os
qt.current_setup='rt2'
qt.reload_current_setup = os.path.join(qt.config['startdir'],"rt2_scripts/setup_rt2.py")

#qt.get_setup_instrument = lambda x: qt.instruments[x] \
#    if qt.config['instance_name'][-3:] == qt.current_setup \
#    else qt.instruments[x+'_'+qt.current_setup]

print 'loading setup tools...'
from measurement.scripts.rt2_scripts.tools import stools
reload(stools)

#print 'reload all modules...'
#execfile(os.path.join(qt.config['startdir'],"reload_all.py"))
from measurement.lib.pulsar import pulse, element, pulsar, pulselib,eom_pulses
reload(pulse)
reload(element)
reload(pulsar)
reload(pulselib)
reload(eom_pulses)

# measurement classes
from measurement.lib.measurement2 import measurement
reload(measurement)

from measurement.lib.measurement2.p7889 import p7889_2d_measurement
reload(p7889_2d_measurement)
####
#print 'reload all measurement parameters and calibrations...'
#from measurement.scripts.lt1_scripts.setup import msmt_params as mcfg
#reload(mcfg)
#qt.exp_params=mcfg.cfg

####
print 'configure the setup-specific hardware...'
# set all the static variables for lt1
execfile(os.path.join(qt.config['startdir'],'rt2_scripts/setup/sequence.py'))

# set all the static variables for lt1
execfile(os.path.join(qt.config['startdir'],'rt2_scripts/setup/rt2_statics.py'))
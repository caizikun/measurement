import os
qt.current_setup='qn1'
qt.reload_current_setup = os.path.join(qt.config['startdir'],"qn1_scripts/setup_qn1.py")

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

print 'loading setup tools...'
from measurement.scripts.lt4_scripts.tools import stools
reload(stools)
qt.stools=stools

print 'reload all modules...'
execfile(os.path.join(qt.config['startdir'],"reload_all.py"))

####
print 'reload all measurement parameters and calibrations...'
from measurement.scripts.lt4_scripts.setup import msmt_params as mcfg
reload(mcfg)
qt.exp_params=mcfg.cfg

####
print 'configure the setup-specific hardware...'
# set all the static variables for lt4
execfile(os.path.join(qt.config['startdir'],'qn1_scripts/setup/sequence.py'))

# set all the static variables for lt4
execfile(os.path.join(qt.config['startdir'],'qn1_scripts/setup/qn1_statics.py'))

import os
qt.current_setup='tel1'
qt.reload_current_setup = os.path.join(qt.config['startdir'],"lt3_scripts/setup_lt3.py")

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

print 'loading setup tools...'
from measurement.scripts.lt3_scripts.tools import stools
reload(stools)
qt.stools=stools

print 'reload all modules...'
execfile(os.path.join(qt.config['startdir'],"reload_all.py"))

####
print 'reload all measurement parameters and calibrations...'
from measurement.scripts.lt3_scripts.setup import msmt_params as mcfg
reload(mcfg)
qt.exp_params=mcfg.cfg

for carbon in qt.instruments.get_instruments_by_type('carbon'):

	### transfer noted parameters from the msmt parameters to the carbon instruments
	carbon.set_carbon_params_from_msmt_params(qt.exp_params,verbose=False)
	### values that were stored in the carbon are now written into exp_params
	carbon.write_attributes_to_msmt_params(qt.exp_params)

####
print 'configure the setup-specific hardware...'
# set all the static variables for tel1
execfile(os.path.join(qt.config['startdir'],'tel1_scripts/setup/tel1_statics.py'))

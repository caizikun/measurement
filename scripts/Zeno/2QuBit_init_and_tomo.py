import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


#logical input state can be one of the six states Z,-Z,X,-X,Y,-Y

def MBE(name, Carbon_list=[1,5],
	carbon_init_list=[5,1],
	carbon_init_states      = 2*['up'], 
	carbon_init_methods     = 2*['swap'], 
	carbon_init_thresholds  = 2*[0],  

	logical_input_state='Z',

	number_of_MBE_steps = 0,
	mbe_bases           = ['X','X'],
	MBE_threshold       = 1,

	number_of_parity_msmnts = 1,
	parity_msmnts_threshold = 1, 

	el_RO_0               = 'positive',
	el_RO_1               = 'negative',
	debug                 = True):

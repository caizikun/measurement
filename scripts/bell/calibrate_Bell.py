

# reload all parameters and modules, import classes
#from measurement.scripts.espin import espin_funcs as funcs
#reload(funcs)

from measurement.scripts.ssro import ssro_calibration
reload(ssro_calibration)
import params
reload(params)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


if __name__ == '__main__':

    ssro_calibration.ssrocalibration('SAMPLE_CFG', **params.params_lt3)

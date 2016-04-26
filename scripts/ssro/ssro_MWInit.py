# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(ps)
from measurement.lib.pulsar import pulselib
reload(pulselib)
execfile(qt.reload_current_setup)

execfile(qt.reload_current_setup)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

"""
Guidelines:

Adjustment to SSRO calibration. Instead of initializing into ms = +-1 via Lasers
initialisation is done into ms = 0 followed by MW pulses.

Order of SSRO calibraiton
    1) ms = 0
    2) ms = +1 (MW1, MW2 out of range)
    3) ms = -1 (MW2)

Have MW1_frequency on ms = +1 freq (Make sure that you 
    put electron transition to +1 in msmt_params so that the MW1 freq is correct)
Have MW2_frequency on ms = -1 freq (2nd MW source can only do -1 due to its range)

Multiplicity of the pulses should be [0, 1, 1]

"""

def ssro_MWInit(name, multiplicity=[0], debug=False, mw2=[False], el_states = ['ms0'], **kw):

    m = pulsar_msmt.SSRO_MWInit(name)
    
    # Import all msmst params
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    # MW settings
    pulse_shape = kw.get('pulse_shape', None)
    if pulse_shape == None:
        pulse_shape == m.params['pulse_shape']
    else:
        m.params['pulse_shape'] = pulse_shape


    m.params['wait_for_AWG_done'] = 1
    # m.params['sequence_wait_time'] = 20
    m.params['send_AWG_start'] = 1
    m.params['pts'] = 1
    
    m.params['repetitions'] = 5000
    m.params['Ex_SP_amplitude']=0

    for mult, mw2, s in zip(multiplicity, mw2, el_states):
        #selecting correct parameters
        m.params['multiplicity'] = mult
        ### need to select the correct frequency


        m.MW_pi = pulse.cp(ps.pi_pulse_MW2(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
        m.autoconfig() 
        m.generate_sequence(upload=True, pulse_pi = m.MW_pi)

        if not debug:
            print 'electron state: ' + str(s)
            m.run(autoconfig=False)
            m.save(s)
    m.finish()

 

if __name__ == '__main__':

    mult = [0,1]#,1]
    mw2  = [False, False]#,True]
    el_states = ['ms0','msp1']#,'msm1']
    debug = False

    stools.turn_off_all_lasers()
    ssro_MWInit(SAMPLE_CFG + '_ssro_MWInit', 
            multiplicity = mult, 
            debug = debug, 
            mw2= mw2, 
            pulse_shape='Hermite',
            el_states = el_states)


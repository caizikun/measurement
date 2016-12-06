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
    2) ms = +1
    3) ms = -1

Have MW1_frequency on ms = +1 freq (Make sure that you 
    put electron transition to +1 in msmt_params so that the MW1 freq is correct)
Have MW2_frequency on ms = -1 freq (2nd MW source can only do -1 due to its range)

Multiplicity of the pulses should be [0, 1, 1]

"""

def ssro_MWInit(name, multiplicity=1, debug=False, mw2=False, **kw):

    m = pulsar_msmt.SSRO_MWInit(name)
    
    # Import all msmst params
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    stools.turn_off_all_lasers()

    # MW settings
    pulse_shape = kw.get('pulse_shape', None)
    if pulse_shape == None:
        pulse_shape == m.params['pulse_shape']
    else:
        m.params['pulse_shape'] = pulse_shape

    m.params['multiplicity'] = np.ones(pts)*multiplicity
    ### need to selectr the correct frequency
    if mw2:
        if m.params['pulse_shape'] == 'Hermite':
            print 'Using Hermite pulses'
            m.params['mw2_duration']            = m.params['mw2_Hermite_pi_length']
            m.params['mw2_pulse_amplitudes']    = m.params['mw2_Hermite_pi_amp'] 
            m.params['MW_pulse_amplitudes']     = m.params['mw2_Hermite_pi_amp'] 
        else:
            print 'Using square pulses'
            m.params['mw2_duration']            =  m.params['mw2_Square_pi_length']
            m.params['mw2_pulse_amplitudes']    = m.params['mw2_Square_pi_amp'] 
            m.params['MW_pulse_amplitudes']     = m.params['mw2_Square_pi_amp'] 
    else:
        if m.params['pulse_shape'] == 'Hermite':
            print 'Using Hermite pulses'
            m.params['MW_duration'] = m.params['Hermite_pi_length']
            m.params['MW_pulse_amplitudes'] = m.params['Hermite_pi_amp']
        else:
            print 'Using square pulses'
            m.params['MW_duration'] =  m.params['Square_pi_length']
            m.params['MW_pulse_amplitudes'] = m.params['Square_pi_amp']


    ### SSRO RO duration sweep params
    #### Maybe not hardcode RO time
    m.params['SSRO_duration_list'] = np.arange(0,500,10)
    m.params['pts'] = len(m.params['SSRO_duration_list'])

    m.params['Ex_SP_amplitude'] = 0.



    m.params['sweep_name'] = 'SSRO_MWInit duration'
    m.params['sweep_pts'] = m.params['SP_duration_list']
    m.params['wait_for_AWG_done'] = 1

    m.MW_pi = pulse.cp(ps.pi_pulse_MW2(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

if __name__ == '__main__':

    mult = [0,1,1]
    mw2  = [False,False,True]
    el_state = ['0','p1','m1']

    for m, mw, s in zip(mult, mw2, el_state):
        ssro_MWInit(SAMPLE_CFG + 'ssro_MWInit_ms' + str(s), 
            multiplicity = m, 
            debug = False, 
            mw2= mw, 
            pulse_shape='Hermite')

execfile(qt.reload_current_setup)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs
# reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
from measurement.lib.pulsar import pulselib

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

"""
This script calibrates pi and pi/2 pulses.
Pulse shape can be Square or Hermite --> the appropriate pulse will be chosen from pulse_select.py.
NOTE: do adjust the MW duration & amplitudes to refer to the proper type of pulse!
"""


def calibrate_scrof_pi_pulse(name, multiplicity=1, debug=False, sweep_pi_2 = False):
    m = pulsar_msmt.ScrofulousPiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pts = 16

    m.params['pulse_type'] = 'Hermite'


    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 600 if multiplicity == 1 else 600
    rng = 0.1 if multiplicity == 1 else 0.02

    ### Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity

    # For square pulses
    m.params['MW_pulse_amplitudes'] = m.params['fast_pi_amp'] + np.linspace(-rng, rng, pts)  
    ### which pulse amplitudes are swept? Is a string containing integers. e.g. '123' sweeps all amplitudes
    m.params['swept_pulses'] = '2'

    
    if sweep_pi_2:
        rng = 0.1
        m.params['MW_pulse_amplitudes'] = m.params['fast_pi2_amp'] + np.linspace(-rng, rng, pts)
        m.params['swept_pulses'] = '13'

    m.params['delay_reps'] = 195 ## Currently not used
    # m.params['mw_power'] = 20 ###put in msmt_params.
    

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = ps.X_pulse(m)
    m.MW_pi2 = ps.Xpi2_pulse(m)
    m.Phi60 = pulse.cp(m.MW_pi2, phase = m.params['Y_phase'])

    # m.Phi60 = pulse.cp(m.MW_pi, phase = m.params['X_phase']+60)
    m.Phi300 = pulse.cp(m.MW_pi, phase = m.params['X_phase'])

    



    print 'amp ', m.params['MW_pulse_amplitudes'][0]
    espin_funcs.finish(m, debug=debug, Phi60=m.Phi60, Phi300 = m.Phi300)



def sweep_number_pi_pulses(name,  debug=False, pts = 30):
    m = pulsar_msmt.GeneralPiCalibration(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['multiplicity'] = np.arange(1, 1 + 2 * pts, 2)
    m.params['pulse_type'] = 'Hermite quantum memory'
    # pts = 10


    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 1000 #if multiplicity == 1 else 5000

    # Pulse settings
    m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    m.params['MW_pulse_amplitudes'] =  np.ones(pts) * m.params['Hermite_fast_pi_amp']  #XXXXX -0.05, 0.05 
    m.params['delay_reps'] = 1000
    m.params['mw_power'] = 20
    

    # for the autoanalysis
    m.params['sweep_name'] = 'Number of pulses'
    m.params['sweep_pts'] = m.params['multiplicity']
    m.params['wait_for_AWG_done'] = 1
    

    # Add Hermite X pulse
    m.MW_pi = hermite_Xpi(m)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)




if __name__ == '__main__':
    calibrate_scrof_pi_pulse(SAMPLE_CFG + 'scrofolous_Pi', multiplicity =15,debug = False)
    # calibrate_scrof_pi_pulse(SAMPLE_CFG + 'BB1_Pi', multiplicity =15,debug = False,sweep_pi_2 = True)

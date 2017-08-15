
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs
# reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
from measurement.lib.pulsar import pulselib

execfile(qt.reload_current_setup)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

"""
This script calibrates pi and pi/2 pulses.
Pulse shape can be Square or Hermite --> the appropriate pulse will be chosen from pulse_select.py.
NOTE: do adjust the MW duration & amplitudes to refer to the proper type of pulse!
"""


def calibrate_BB1_pi_pulse(name, multiplicity=1, debug=False):
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
    rng = 0.2 if multiplicity == 1 else 0.08

    ### Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity

    # For square pulses
    m.params['MW_pulse_amplitudes'] = m.params['BB1_fast_pi_amp'] + np.linspace(-rng, rng, pts)  
    ### which pulse amplitudes are swept? Is a string containing integers. e.g. '123' sweeps all amplitudes
    m.params['swept_pulses'] = '12345'

    
    m.params['delay_reps'] = 1#195 ## Currently not used    

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = ps.X_pulse(m)
    m.MW_pi = pulse.cp(m.MW_pi,length = m.params['BB1_fast_pi_duration'], amplitude = m.params['BB1_fast_pi_amp'])
    m.MW_pi2 = ps.Xpi2_pulse(m)

    # m.Phi60 = pulse.cp(m.MW_pi, phase = m.params['X_phase']+60)
    
    ### scrofolous pulse: https://arxiv.org/pdf/quant-ph/0208092.pdf
    m.Phi1 = pulse.cp(m.MW_pi, phase = 60)
    m.Phi2 = pulse.cp(m.MW_pi, phase = 300)
    m.params['composite_pulse_keys'] = ['1','2','1']
    m.pulse_dict = {'1': m.Phi1,'2' : m.Phi2} ### keys refer to composite_pulse_keys



    #### BB1 pulse is below
    # m.Phi1 = pulse.cp(m.MW_pi, phase = m.params['X_phase']+104.5)
    # m.Phi2 = pulse.cp(m.MW_pi, phase = m.params['X_phase']+313.4)
    # m.Phi3 = pulse.cp(m.MW_pi, phase = m.params['X_phase'])
    # m.params['composite_pulse_keys'] = ['1','2','2','1','3'] ### determines what pulse you want to do in which oder
    # m.pulse_dict = {'1': m.Phi1,'2' : m.Phi2,'3' : m.Phi3} ### keys refer to composite_pulse_keys
    

    print 'amp ', m.params['MW_pulse_amplitudes'][0]
    espin_funcs.finish(m, debug=debug, pulse_dict = m.pulse_dict)



def sweep_number_pi_pulses(name,debug = False, pts = 30):
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
    calibrate_BB1_pi_pulse(SAMPLE_CFG + 'BB1_Pi', multiplicity =11, debug = False)

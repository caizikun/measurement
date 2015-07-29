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


def calibrate_pi_pulse(name, multiplicity=1, debug=False, sweep_range=0.03):
    m = pulsar_msmt.GeneralPiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite quantum memory'
    # m.params['pulse_type'] = 'Square quantum memory'
    pts = 11

    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 1500 if multiplicity == 1 else 1500

    ### Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity

    # For square pulses
    m.params['MW_duration'] = m.params['fast_pi_duration']
    m.params['MW_pulse_amplitudes'] = m.params['fast_pi_amp'] + np.linspace(-sweep_range, sweep_range, pts)  #XXXXX -0.05, 0.05 
    
    # For hermite pulses
    # m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    # m.params['MW_pulse_amplitudes'] =  m.params['Hermite_fast_pi_amp'] + np.linspace(-0.04, 0.02, pts)  #XXXXX -0.05, 0.05 

    m.params['delay_reps'] = 195 ## Currently not used
    m.params['mw_power'] = 20
    

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = ps.Y_pulse(m)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

def pi_pulse_sweepdelay_singleelement(name, multiplicity=1, debug=False):
    m = pulsar_msmt.PiCalibrationSingleElement_SweepDelay(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite quantum memory'
    # m.params['pulse_type'] = 'Square quantum memory'
    pts = 21

    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 3000 if multiplicity == 1 else 3000

    # Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    m.params['MW_pulse_amplitudes'] =  m.params['Hermite_fast_pi_amp'] * np.ones(pts)
    m.params['interpulse_delay'] = np.linspace(0.1,200.1,pts) * 1e-6

    m.params['mw_power'] = 20
    

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
   
    m.params['sweep_pts'] = m.params['interpulse_delay'] * 1e6
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = ps.X_pulse(m)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

def pi_pulse_sweepdelay(name, multiplicity=1, debug=False):
    m = pulsar_msmt.PiCalibration_SweepDelay(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite quantum memory'
    # m.params['pulse_type'] = 'Square quantum memory'
    pts = 21

    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 1000 if multiplicity == 1 else 5000

    # Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    m.params['MW_pulse_amplitudes'] =  m.params['Hermite_fast_pi_amp'] * np.ones(pts)
    
    m.params['delay_reps'] = np.linspace(1,100,pts)

    m.params['mw_power'] = 20
    

    # for the autoanalysis
    m.params['sweep_name'] = 'Interpulse delay (us)'
   
    m.params['sweep_pts'] = m.params['interpulse_delay'] * 1e6
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = ps.X_pulse(m)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

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

def calibrate_pi2_pulse(name, debug=False):
    m = pulsar_msmt.GeneralPi2Calibration(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    print 'pulse_shape =', m.params['pulse_shape']

    pts = 11
    m.params['pulse_type'] = 'Square QuMem'    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 1500

    # Append pi & pi/2 pulses to instance
    m.MW_pi = ps.X_pulse(m)

    m.MW_pi2 = ps.Xpi2_pulse(m)

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    m.params['Ex_SP_amplitude']=0
    # m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    # Square pulses
    sweep_axis =  m.params['fast_pi2_amp'] + np.linspace(-0.1, 0.1, pts)  
    m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # Hermite pulses
    # sweep_axis =  m.params['Hermite_fast_pi2_amp'] + np.linspace(-0.01, 0.01, pts)  
    # m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    espin_funcs.finish(m, debug = debug, pulse_pi = m.MW_pi, pulse_pi2 = m.MW_pi2)

def hermite_Xpi(msmt):
    
    # MW_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
    #                      'MW_Imod',
    #                      'MW_Qmod',
    #                      'MW_pulsemod',
    #                      frequency =  #msmt.params['fast_pi_mod_frq'],
    #                      amplitude = #msmt.params['fast_pi_amp'],
    #                      length = #msmt.params['fast_pi_duration'],
    #                      PM_risetime = msmt.params['MW_pulse_mod_risetime'],
    #                      pi2_pulse = False)

    # Pi pulse for DarkESR
    MW_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                         'MW_Imod',
                         'MW_Qmod',
                         'MW_pulsemod',
                         Sw_channel = 'MW_switch',
                         frequency = msmt.params['Hermite_fast_pi_mod_frq'], #msmt.params['fast_pi_mod_frq'],
                         amplitude = msmt.params['Hermite_fast_pi_amp'],  #msmt.params['fast_pi_amp'],
                         length = msmt.params['MW_duration'],
                         PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                         Sw_risetime = msmt.params['MW_switch_risetime'],
                         pi2_pulse = False)

    print 'Sw_channel =', MW_pi.Sw_channel

    return MW_pi 

if __name__ == '__main__':
    #calibrate_pi_pulse(SAMPLE_CFG + 'QuanMem_Pi', multiplicity = 7, sweep_range=0.03)
    # pi_pulse_sweepdelay_singleelement(SAMPLE_CFG + 'QuanMem_Pi', multiplicity = 2)
    # sweep_number_pi_pulses(SAMPLE_CFG + 'QuanMem_Pi',pts=10)
    calibrate_pi2_pulse(SAMPLE_CFG + 'QuMem_Pi2', debug = False)
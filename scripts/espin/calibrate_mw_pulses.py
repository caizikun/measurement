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
This script calibrates pi and pi/2 pulses.
Pulse shape can be Square or Hermite --> the appropriate pulse will be chosen from pulse_select.py.
NOTE: do adjust the MW duration & amplitudes to refer to the proper type of pulse!
"""


def calibrate_pi_pulse(name, multiplicity=1, debug=False, mw2=False, **kw):

    
    m = pulsar_msmt.GeneralPiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pulse_shape = m.params['pulse_shape']
    pts = 12

    m.params['pts'] = pts
    
    ps.X_pulse(m) #### update the pulse params depending on the chosen pulse shape.

    m.params['repetitions'] = 600 if multiplicity == 1 else 500
    rng = 0.2 if multiplicity == 1 else 0.02


    ### comment NK: the previous parameters for MW_duration etc. were not used anywhere in the underlying measurement class.
    ###             therefore, I removed them
    if mw2:
        m.params['MW_pulse_amplitudes'] = m.params['mw2_fast_pi_amp'] + np.linspace(-rng, rng, pts)
    else: 
        m.params['MW_pulse_amplitudes'] = m.params['fast_pi_amp'] + np.linspace(-rng, rng, pts)  
            
            
    
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['delay_reps'] = 0
    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    m.MW_pi = pulse.cp(ps.mw2_X_pulse(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

def calibrate_theta_pulse(name, multiplicity=1, debug=False, mw2=False, **kw):

    
    m = pulsar_msmt.GeneralPiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pulse_shape = m.params['pulse_shape']
    pts = 12

    m.params['pts'] = pts
    
    ps.X_pulse(m) #### update the pulse params depending on the chosen pulse shape.

    m.params['repetitions'] = 5000
    rng = kw.pop('rng',0.2)

    m.params['MW_pulse_amplitudes'] = m.params['Hermite_theta_amp'] + np.linspace(-rng, rng, pts)  
            
            
    
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['delay_reps'] = 0
    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    m.MW_pi = pulse.cp(ps.Xpi2_pulse(m),phase = 0)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)


def calibrate_pi_pulse_NoIQSource(name, multiplicity=1, debug=False):
    m = pulsar_msmt.General_mw2_PiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite quantum memory'
    # m.params['pulse_type'] = 'Square quantum memory'
    pts = 16

    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 600
    rng = 8e-9 if multiplicity == 1 else 4e-9

    ### Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity

    # For square pulses
    m.params['MW2_duration'] = m.params['mw2_fast_pi_duration'] + np.linspace( - rng, rng, pts)
    m.params['MW2_pulse_amplitudes'] = m.params['mw2_fast_pi_amp']   #XXXXX -0.05, 0.05 
    
    # For hermite pulses
    # m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    # m.params['MW_pulse_amplitudes'] =  m.params['Hermite_fast_pi_amp'] + np.linspace(-0.04, 0.02, pts)  #XXXXX -0.05, 0.05 

    m.params['delay_reps'] = 195 ## Currently not used
    # m.params['mw_power'] = 20 ###put in msmt_params.
    

    # for the autoanalysis
    m.params['sweep_name'] = 'MW duration (ns)'
   
    m.params['sweep_pts'] = m.params['MW2_duration']*1e9
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    # m.MW_pi = hermite_Xpi(m)
    m.MW_pi = pulse.cp(ps.pi_pulse_MW2(m),phase = 0)

    print 'amplitude ', m.params['MW2_pulse_amplitudes']
    print 'duration ', m.params['MW2_duration'][0]
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
    pts = 11

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
    
    m.MW_pi = ps.X_pulse(m)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi)

def calibrate_pi2_pulse(name, debug=False,mw2=False):
    m = pulsar_msmt.GeneralPi2Calibration(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pts = 11
    m.params['pulse_type'] = 'Hermite'    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 1000

    if mw2:
        print m.params['mw2_pulse_shape']
        m.MW_pi = ps.mw2_X_pulse(m)
        m.MW_pi2 = ps.mw2_Xpi2_pulse(m)
        sweep_axis =  m.params['mw2_Hermite_pi2_amp'] + np.linspace(-0.12, 0.12, pts)  
        m.params['pulse_pi2_sweep_amps'] = sweep_axis        
    else:
        print m.params['pulse_shape']
        m.MW_pi=ps.X_pulse(m)
        m.MW_pi2=ps.Xpi2_pulse(m)
        sweep_axis =  m.params['Hermite_pi2_amp'] + np.linspace(-0.12, 0.12, pts)  
        m.params['pulse_pi2_sweep_amps'] = sweep_axis


    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts

    m.params['Ex_SP_amplitude']=0
    # m.params['SP_duration'] = 50
    m.params['wait_for_AWG_done'] = 1

    # Square pulses
    # sweep_axis =  m.params['fast_pi2_amp'] + np.linspace(-0.02, 0.02, pts)  
    # m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    espin_funcs.finish(m, debug = debug, pulse_pi = m.MW_pi, pulse_pi2 = m.MW_pi2)


def calibrate_comp_pi2_pi_pi2_pulse(name, multiplicity=1, debug=False):
    m = pulsar_msmt.CompositePiCalibrationSingleElement(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite composite'
    # m.params['pulse_type'] = 'Square quantum memory'
    pts = 16

    m.params['pts'] = pts
    # m.params['repetitions'] = 3000 if multiplicity == 1 else 5000
    m.params['repetitions'] = 600
    rng = 0.1 if multiplicity == 1 else 0.08

    ### Pulse settings
    m.params['multiplicity'] = np.ones(pts)*multiplicity

    # For square pulses
    #m.params['MW_duration'] = m.params['Hermite_fast_pi_duration']
    m.params['MW_pulse_amplitudes'] = m.params['Hermite_pi_amp'] + np.linspace(-rng, rng, pts)
    
    m.params['delay_reps'] = 195 ## Currently not used
    

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    # Add Hermite X pulse
    
    m.comp_pi = pulse.cp(ps.comp_pi2_pi_pi2_pulse(m),phase = 0)
    # m.comp_pi = pulse.cp(ps.X_pulse(m),phase = 0)

    #print 'duration ', m.params['MW_duration']
    print 'amp ', m.params['MW_pulse_amplitudes'][0]
    espin_funcs.finish(m, debug=debug, pulse_pi=m.comp_pi)

def sweep_pm_risetime(name, debug=False, mw2=False, **kw):
    m = pulsar_msmt.Sweep_pm_risetime(name)
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    pulse_shape = 'Square'
    m.params['pulse_shape'] = pulse_shape
    m.params['pulse_type'] = pulse_shape
   

    pts =20
    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    min_risetime = 0e-9
    max_risetime = 100e-9

    m.params['PM_risetime_sweep'] = np.linspace(min_risetime, max_risetime, pts)

    m.params['delay_reps'] = 195 ## Currently not used
    # for the autoanalysis
    m.params['sweep_name'] = 'PM risetime (ns)'
   
    m.params['sweep_pts'] = m.params['PM_risetime_sweep']*1e9
    m.params['wait_for_AWG_done'] = 1

    espin_funcs.finish(m, debug=debug, mw2=mw2)

if __name__ == '__main__':
    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =15, debug = False, mw2=False)
    calibrate_theta_pulse(SAMPLE_CFG + 'theta', debug = False, rng = 0.05)
    #sweep_pm_risetimexe(SAMPLE_CFG + 'PMrisetime', debug = False, mw2=True) #Needs calibrated square pulses
    #pi_pulse_sweepdelay_singleelement(SAMPLE_CFG + 'QuanMem_Pi', multiplicity = 2)
    #sweep_number_pi_pulses(SAMPLE_CFG + 'QuanMem_Pi',pts=10)
    # calibrate_pi2_pulse(SAMPLE_CFG + 'Hermite_Pi2', debug = False, mw2=False)
    #calibrate_comp_pi2_pi_pi2_pulse(SAMPLE_CFG + 'Hermite_composite_pi',multiplicity=1, debug=False)

# Calibration steps for the Bell test experiment


from measurement.scripts.bell.calibrations import bell_funcs
reload(bell_funcs)



### called at stage 2.0
def rabi(name, IQmod=True, **kw):
	'''
	Rabi oscillations on the 0 <-> -1 transition.
	You can choose either to use normal square pulses or IQ modulation pulses\n
	by setting the IQmod parameter.
	Available keywords : 
		- 'pts' (default value = 21)
		- 'sweep_MW_amplitude' : to sweep either the MW pulse amplitude \n
		or the MW pulse duration (default value = True)
			- If sweep_MW_amplitude == True, available parameters :
				- 'MW_pulse_amplitude_min' in V (default value = 0.0 V)
				- 'MW_pulse_amplitude_max' in V (default value = 0.1 V)
				- 'MW_pulse_fixed_duration' in s (default value = 100 ns)
			- If sweep_MW_amplitude == False, available parameters :
				- 'MW_pulse_duration_min' in s (default value = 0 ns)
				- 'MW_pulse_duration_max' in s (default value = 100 ns)
				- 'MW_pulse_fixed_amplitude' in V (default value = 0.05 V)
	'''

    if IQmod :
        m = pulsar_msmt.ElectronRabi(name)
    else :
        m = pulsar_msmt.ElectronRabi_Square(name)
   
    # add later params.params_lt3 !!!!
    funcs.prepare(m)

    pts = kw.pop('pts', 21)
    sweep_MW_amplitude = kw.pop('sweep_MW_amplitude', True )

    MW_pulse_amplitude_min = kw.pop('MW_pulse_amplitude_min', 0.0 ) # in V
    MW_pulse_amplitude_max = kw.pop('MW_pulse_amplitude_max', 0.1 ) # in V
    MW_pulse_fixed_duration = kw.pop('MW_pulse_fixed_duration', 100e-9) # in s

    MW_pulse_duration_min = kw.pop('MW_pulse_duration_min', 0.0e-9 ) # in s
    MW_pulse_duration_max = kw.pop('MW_pulse_duration_max', 100e-9 ) # in s
    MW_pulse_fixed_amplitude = kw.pop('MW_pulse_fixed_amplitude', 0.05) # in V


    m.params['pts'] = pts
    m.params['repetitions'] = 1000
	m.params['Ex_SP_amplitude'] = 0 # no SP from ms=0 to ms=1

    if IQmod :
        m.params['MW_pulse_frequency'] = 43e6 # this name changes a lot 
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_pulse_frequency'] 
    else :
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 
    print 'IQ modulation : {0}'.format(IQmod)
    print 'The effective MW frequency is : {:.6f} GHz'.format(m.params['ms-1_cntr_frq']*1e-9)  

    if sweep_MW_amplitude : 
    	m.params['MW_pulse_amplitudes'] = np.linspace(MW_pulse_amplitude_min, MW_pulse_amplitude_max, pts)
    	m.params['MW_pulse_durations'] = np.ones(pts)*MW_pulse_fixed_duration
    	m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
		m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
	else : # sweep the MW pulse durations
		m.params['MW_pulse_durations'] = np.linspace(MW_pulse_duration_min, MW_pulse_duration_max, pts)
		m.params['MW_pulse_amplitudes'] = np.ones(pts)*MW_pulse_fixed_amplitude
		m.params['sweep_name'] = 'Pulse durations (ns)'
    	m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    
    print 'sweep pts : ', m.params['sweep_pts']


    funcs.finish(m, upload=True, debug=False)


    print "\nAnalysis suggestion : execfile(r'D:\measuring\\analysis\scripts\espin\electron_rabi_analysis.py')"


### called at stage 2.5
def dark_esr(name, **kw):
    '''
    dark ESR on the 0 <-> -1 transition. This function uses IQ mod pulses.
    The range center frequency is set by the 'ms-1_cntr_frq' parameter 
    in the parameter dictionary. 
    Available keywords :
    	- 'pts' (default value = 131)
    	- 'MW_range' in Hz (default value = 10 MHz)
    	- 'MW_pulse_duration' in s (default value = 2 us)
    	- 'MW_pulse_amplitude' in V (default value = 0.03 V)
    '''

    m = pulsar_msmt.DarkESR(name)
    funcs.prepare(m)

    pts = kw.pop('pts', 131)
    MW_range = kw.pop('MW_range', 10e6)
    MW_pulse_duration = kw.pop('MW_pulse_duration', 2e-6) # in s
    MW_pulse_amplitude = kw.pop('MW_pulse_amplitude', 0.03) # in V


    m.params['ssmod_detuning']   = 43e6
    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']      = 1000
    m.params['range']            = MW_range
    m.params['pts']              = pts
    m.params['pulse_length']     = MW_pulse_duration
    m.params['ssbmod_amplitude'] = MW_pulse_amplitude
    
    m.params['Ex_SP_amplitude'] = 0 # no SP from ms=0 to ms=1


    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']


    funcs.finish(m, upload=True, debug=False)


### master function
def run_calibrations(stage, IQmod): 


    if stage == 0 : # Continuous ESR -> to get coarse ESR frequency
        print "\nFirst measure the resonance frequency with a continuous ESR : \n \
        execfile(r'D:/measuring/scripts/espin/esr.py') \n \
        Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/simple_esr_fit.py')"

    if stage == 1 : #SSRO
        ssro_calibration.ssrocalibration('SAMPLE_CFG', **params.params_lt3)

    if stage == 2.0 : # slow Rabi frequency -> to get pi pulse for dark ESR
        rabi(SAMPLE+'_'+'rabi', IQmod=IQmod, pts = 21, sweep_MW_amplitude = True, 
        	MW_pulse_amplitude_min = 0.0, MW_pulse_amplitude_max = 0.05,
        	MW_pulse_fixed_duration = 2e-6)

    if stage == 2.5 : #  dark ESR
        print "Starting a dark ESR spectrum"
        dark_esr(SAMPLE_CFG, pts = 131, MW_range = 6e6, 
        	MW_pulse_duration = 2e-6, MW_pulse_amplitude = 0.03)
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/dark_esr_analysis.py')"
 
 	# fast Rabi oscillation -> get the coarse voltage for the CORPSE pi pulse
    if stage == 3.0 : # first, MW pulse duration sweep -> get an idea of the maximum available Rabi frequency
		rabi(SAMPLE+'_'+'rabi', IQmod=IQmod, pts = 21, sweep_MW_amplitude = False, 
        	MW_pulse_duration_min = 0e-9, MW_pulse_duration_max = 50e-9,
        	MW_pulse_fixed_amplitude = 0.9)
	if stage == 3.5 : 
		rabi(SAMPLE+'_'+'rabi', IQmod=IQmod, pts = 21, sweep_MW_amplitude = True, 
        	MW_pulse_amplitude_min = 0.0, MW_pulse_amplitude_max = 0.05,
        	MW_pulse_fixed_duration = 2e-6)

    if stage == 3.0 :
        calibrate_Pi_CORPSE(SAMPLE_CFG, IQmod = IQmod )
    if stage == 3.5 :
        calibrate_Pi_CORPSE(SAMPLE_CFG, IQmod = IQmod, multiplicity = 8)
    if stage == 3.75:
        dark_esr_Corpse(SAMPLE_CFG)

    if stage == 4.0 :
        calibrate_Pi2_CORPSE(SAMPLE_CFG, IQmod = IQmod )

    if stage == 5.0 :
        #!!! change the Ramsey class to allow to choose between normal pulses
        # and CORPSE ones, issue with length of normal pulses
        Corpse = False
        ramsey_Corpse(SAMPLE_CFG, IQmod = IQmod, Corpse = Corpse)


    if stage == 6.0 :
        dd_Corpse_zerothrevival(SAMPLE_CFG, IQmod = IQmod)
    if stage == 6.5 :
        dd_zerothrevival(SAMPLE_CFG, IQmod = IQmod)



if __name__ == '__main__':
    run_calibrations(3.0, IQmod = False)



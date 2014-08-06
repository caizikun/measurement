pi2_len = 84
pi_len 	= 160

C1_freq    = 345.124e3   
C1_freq_0  = 325.787e3  
C1_Ren_tau = 9.420e-6
C1_Ren_N   = 18

C4_freq    = 348.574e3   
C4_freq_0  = 325.787e3 
C4_Ren_tau = 6.456e-6 
C4_Ren_N   = 40  


def get_periods_phase(carbon, time, time0=0):
	if carbon == 4:
		periods = (C4_freq*(time-time0) + C4_freq_0*time0)*1e-9
		phase   = mod(periods*360,360)
	elif carbon == 1:
		periods = (C1_freq*(time-time0) + C1_freq_0*time0)*1e-9
		phase   = mod(periods*360,360)

	return periods, phase


### Carbon 4 Ren
Ren_4_len 					= 958 + 5e3 + 1912 + 39*10e3 + 38*2912 + 1912 + 5e3 + 958 + pi2_len
Ren_4_len_ideal 			= 2*C4_Ren_tau*C4_Ren_N*1e9
Ren_4_periods, Ren_4_phase 	= get_periods_phase(4, Ren_4_len)

if 0:
	print 'Ren_4_len_ideal = ' 	+str(Ren_4_len_ideal) 
	print 'Ren_4_len = ' 		+str(Ren_4_len) 
	print 'Ren_4_periods = '    +str(Ren_4_periods)
	print 'Ren_4_phase = ' 		+str(Ren_4_phase)
	print 'conclusion : all correct'

#######################
### ZZ state, RO ZI ###
#######################

if 0:
	### Carbon 4 phases: 
	### between Ren4_1 - Ren4_2 (count from end pi to start pi, then add pi length and remove 2*tau)
	t_Ren4_1 = 376 + 5e3 + 5584 + 5e3 + 376 + 2.*pi_len/2. - 2*C4_Ren_tau
	t_Ren4_1_periods, t_Ren4_1_phase 	= get_periods_phase(4, t_Ren4_1)

	t_Ren4_2 = (376 + 5e3 + 116e3 + 2e3 + 
			    8e3 + 1840 + 17*16e3 + 16*2840 + 1840 + 8e3 + 5624 + 
			    8e3 + 1840 + 17*16e3 + 16*2840 + 1840 + 8e3 + 116e3 + 6264 +
			    5e3 + 376 + 2.*pi_len/2. - 2*C4_Ren_tau)

	t_Ren4_2_0 = (376 + 5e3 + 116e3 + 958 + pi_len/2. + pi2_len/2. - C4_Ren_tau +
				  340 + 8e3 + 116e3 + 1188 + pi_len/2. + pi_len/2. - C1_Ren_tau -  1348/2.)  ### The time that the electron was in 0 instead of being DDed
	t_Ren4_2_periods, t_Ren4_2_phase 	= get_periods_phase(4, t_Ren4_2, t_Ren4_2_0)

	t_Ren4_3 = 376 + 5e3 + 5584 + 5e3 + 376 + 2*pi_len/2. - 2*C4_Ren_tau 
	t_Ren4_3_periods, t_Ren4_3_phase 	= get_periods_phase(4, t_Ren4_3)

		### Carbon 1 phases: 
	t_Ren1_1 = 340 + 8e3 + 5624 + 8e3 + 340 + 2.*pi_len/2. - 2*C1_Ren_tau
	t_Ren1_1_periods, t_Ren1_1_phase 	= get_periods_phase(1, t_Ren1_1)
		

	if 1:
		print 't_Ren4_1 = ' 			+str(t_Ren4_1) 
		print 't_Ren4_1_periods = ' 	+str(t_Ren4_1_periods) 
		print 't_Ren4_1_phase = ' 		+str(t_Ren4_1_phase) 
		print
		print 't_Ren4_2 = ' 			+str(t_Ren4_2) 
		print 't_Ren4_2_periods = ' 	+str(t_Ren4_2_periods) 
		print 't_Ren4_2_phase = ' 		+str(t_Ren4_2_phase) 
		print
		print 't_Ren4_3 = ' 			+str(t_Ren4_3) 
		print 't_Ren4_3_periods = ' 	+str(t_Ren4_3_periods) 
		print 't_Ren4_3_phase = ' 		+str(t_Ren4_3_phase) 
		print
		print 't_Ren1_1 = ' 			+str(t_Ren1_1) 
		print 't_Ren1_1_periods = ' 	+str(t_Ren1_1_periods) 
		print 't_Ren1_1_phase = ' 		+str(t_Ren1_1_phase) 

######################
### ZZ state, RO IZ###
######################

	### Carbon 4 phases: 
t_Ren4_1 = 376 + 5e3 + 5584 + 5e3 + 376 + 2.*pi_len/2. - 2*C4_Ren_tau
t_Ren4_1_periods, t_Ren4_1_phase 	= get_periods_phase(4, t_Ren4_1)

	### Carbon 1 phases: 
t_Ren1_1 = 340 + 8e3 + 5624 + 8e3 + 340 + 2.*pi_len/2. - 2*C1_Ren_tau
t_Ren1_1_periods, t_Ren1_1_phase 	= get_periods_phase(1, t_Ren1_1)

t_Ren1_2 	= 340 + 8e3 + 116e3 + 4776 + 8e3 + 340 
t_Ren1_2_0 	= 340 + 8e3 + 116e3 + 1268 + 2*pi_len/2 - C1_Ren_tau - 694/2. ### The time that the electron was in 0 instead of being DDed
t_Ren1_2_periods, t_Ren1_2_phase 	= get_periods_phase(1, t_Ren1_2, t_Ren1_2_0)

	### Carbon 1 phases: 
t_Ren1_3 = 340 + 8e3 + 5624 + 8e3 + 340 + 2.*pi_len/2. - 2*C1_Ren_tau
t_Ren1_3_periods, t_Ren1_3_phase 	= get_periods_phase(1, t_Ren1_3)



if 1:
	print 't_Ren4_1 = ' 			+str(t_Ren4_1) 
	print 't_Ren4_1_periods = ' 	+str(t_Ren4_1_periods) 
	print 't_Ren4_1_phase = ' 		+str(t_Ren4_1_phase) 
	print
	print 't_Ren1_1 = ' 			+str(t_Ren1_1) 
	print 't_Ren1_1_periods = ' 	+str(t_Ren1_1_periods) 
	print 't_Ren1_1_phase = ' 		+str(t_Ren1_1_phase) 
	print
	print 't_Ren1_2 = ' 			+str(t_Ren1_2) 
	print 't_Ren1_2_periods = ' 	+str(t_Ren1_2_periods) 
	print 't_Ren1_2_phase = ' 		+str(t_Ren1_2_phase) 
	print
	print 't_Ren1_3 = ' 			+str(t_Ren1_3) 
	print 't_Ren1_3_periods = ' 	+str(t_Ren1_3_periods) 
	print 't_Ren1_3_phase = ' 		+str(t_Ren1_3_phase) 




	
qt.multi_tau_carbon_dict = {}
if qt.current_setup == 'lt3':


	#######################
	#### SIL 1 ###########
	#####################
	# qt.multi_tau_carbon_dict['C2'] = {'C_taus' 	: [4.51e-6], 
	# 								'C_tau_rng'  :10e-9, # steps of 2e-9
	# 								'C_N' 		: [48],
	# 								'C_N_steps' : 8} # steps of 2 	


	# qt.multi_tau_carbon_dict['C3'] = {'C_taus' 	: [7.144e-6],#,8.244e-6,9.34e-6,12.638e-6,21.428e-6], 
	# 								'C_tau_rng'  :0e-9, # steps of 2e-9
	# 								'C_N' 		: [38],
	# 								'C_N_steps' : 8} # steps of 2 	

	# #sweep parameters C4
	# # qt.multi_tau_carbon_dict['C4'] = {'C_taus' 	: [9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
	# # 								'C_tau_rng'  :20e-9, # steps of 2e-9
	# # 								'C_N' 		: [28],
	# # 								'C_N_steps' : 12} # steps of 2 	


	# # sweep parameters C5
	# qt.multi_tau_carbon_dict['C5'] = {'C_taus' 	: [7.08e-6], #6.25e-6, 9.66e-6, 15.345e-6, 19.920e-6],#22.165e-6], # m1[7.108e-6],#[9.3e-6, 14.77e-6,16.96e-6,18.053e-6],
	# 								'C_tau_rng'  :10e-9, # steps of 2e-9
	# 								'C_N' 		: [28],
	# 								'C_N_steps' : 8} # steps of 2 	


	# #sweep parameters C6
	# qt.multi_tau_carbon_dict['C6'] = {'C_taus' 	: [16.065e-6],#[6.17e-6,9.355e-6,19.625e-6],#[17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
	#  								'C_tau_rng' : 10e-9,
	# 								'C_N' 		: [24], 
	# 								'C_N_steps' : 8} 

	# #sweep parameters C7
	# qt.multi_tau_carbon_dict['C7'] = {'C_taus' 	: [8.628e-6],
	#  								'C_tau_rng' : 10e-9,
	# 								'C_N' 		: [24], 
	# 								'C_N_steps' : 8} 

	# qt.multi_tau_carbon_dict['C8'] = {'C_taus' 	: [4.818e-6],
	#  								'C_tau_rng' : 10e-9,
	# 								'C_N' 		: [20], 
	# 								'C_N_steps' : 8} 

	#######################
	#### SIL 2 ###########
	#####################
	# qt.multi_tau_carbon_dict['C1'] = {'C_taus' 	: [10.884e-6],#[8.592e-6, 10.884e-6,6.3e-6,7.476e-6,9.76e-6,13.142e-6, 15.46e-6], 
	# 								'C_tau_rng' : 14e-9, # steps of 2e-9
	# 								'C_N' 		: [12],#[10,10,10,10,10,10,14],
	# 								'C_N_steps' : 6} # steps of 2 	

	# qt.multi_tau_carbon_dict['C2'] = {'C_taus' 	: [9.318e-6,10.786e-6,11.92e-6,13.05e-6,14.19e-6,16.46e-6,22.14e-6], 
	# 								'C_tau_rng' : 12e-9, # steps of 2e-9
	# 								'C_N' 		: [24,24,22,24,26,26,42],
	# 								'C_N_steps' : 10} # steps of 2 	
	#######################
	#### SIL 3 ###########
	#####################
	qt.multi_tau_carbon_dict['C1'] = {'C_taus' 	: [6.302e-6],#[8.592e-6, 10.884e-6,6.3e-6,7.476e-6,9.76e-6,13.142e-6, 15.46e-6], 
									'C_tau_rng' : 14e-9, # steps of 2e-9
									'C_N' 		: [30],#[10,10,10,10,10,10,14],
									'C_N_steps' : 12} # steps of 2 	

	qt.multi_tau_carbon_dict['C2'] = {'C_taus' 	: [6.356e-6], 
									'C_tau_rng' : 8e-9, # steps of 2e-9
									'C_N' 		: [58],
									'C_N_steps' : 8} # steps of 2 	
									

elif qt.current_setup == 'lt4':

	### -1 transition
	# qt.multi_tau_carbon_dict['C1'] = {'C_taus' 	: [4.900e-6], 
	# 								'C_tau_rng'  :16e-9, # steps of 2e-9
	# 								'C_N' 		: [38],
	# 								'C_N_steps' : 12} # steps of 2 	

	# qt.multi_tau_carbon_dict['C2'] = {'C_taus' 	: [4.900e-6], 
	# 								'C_tau_rng'  :16e-9, # steps of 2e-9
	# 								'C_N' 		: [38],
	# 								'C_N_steps' : 12} # steps of 2 	


	# qt.multi_tau_carbon_dict['C3'] = {'C_taus' 	: [3.688e-6,13.18e-6], 
	# 								'C_tau_rng'  :10e-9, # steps of 2e-9
	# 								'C_N' 		: [64,58],
	# 								'C_N_steps' : 12} # steps of 2 	

	
	# qt.multi_tau_carbon_dict['C4'] = {'C_taus' 	: [6.402e-6],#,5.230e-6,7560e-9,8720e-9],#[5.274e-6, 6.464e-6, 7.64e-6, 8.82e-6], 
	# 								'C_tau_rng'  : 12e-9, # steps of 2e-9
	# 								'C_N' 		: [28],#,24,26,30], 
	# 								'C_N_steps' : 12} # steps of 2 	


	# qt.multi_tau_carbon_dict['C5'] = {'C_taus' 	: [8.656e-6],#[5.22e-6],#[6.4e-6, 8.73e-6]
	# 								'C_tau_rng'  :16e-9, # steps of 2e-9
	# 								'C_N' 		: [40],#[36,44], # 34,
	# 								'C_N_steps' : 12} # steps of 2 	


	# qt.multi_tau_carbon_dict['C6'] = {'C_taus' 	: [3.626e-6,4.664e-6,8.812e-6],#[6.17e-6,9.355e-6,19.625e-6],#[17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
	#  								'C_tau_rng' : 10e-9,
	# 								'C_N' 		: [42,70,52], 
	# 								'C_N_steps' : 12} 


	# qt.multi_tau_carbon_dict['C7'] = {'C_taus' 	: [12.796e-6,17.246e-6], #9.458e-6,11.682e-6,
	#  								'C_tau_rng' : 10e-9,
	# 								'C_N' 		: [60,62], #56,62,
	# 								'C_N_steps' : 12} 


	qt.multi_tau_carbon_dict['C1'] = {'C_taus' 	: [10.3e-6], 
									'C_tau_rng'  :30e-9, # steps of 2e-9
									'C_N' 		: [4],
									'C_N_steps' : 2} # steps of 2 	

	qt.multi_tau_carbon_dict['C2'] = {'C_taus' 	: [8.766e-6], 
									'C_tau_rng'  :10e-9, # steps of 2e-9
									'C_N' 		: [42],
									'C_N_steps' : 12} # steps of 2 	


	qt.multi_tau_carbon_dict['C3'] = {'C_taus' 	: [11.514e-6], 
									'C_tau_rng'  :10e-9, # steps of 2e-9
									'C_N' 		: [50],
									'C_N_steps' : 12} # steps of 2 	

	
	qt.multi_tau_carbon_dict['C4'] = {'C_taus' 	: [11.564e-6],#,5.230e-6,7560e-9,8720e-9],#[5.274e-6, 6.464e-6, 7.64e-6, 8.82e-6], 
									'C_tau_rng'  : 12e-9, # steps of 2e-9
									'C_N' 		: [42],#,24,26,30], 
									'C_N_steps' : 12} # steps of 2 	


	qt.multi_tau_carbon_dict['C5'] = {'C_taus' 	: [11.474e-6],#[5.22e-6],#[6.4e-6, 8.73e-6]
									'C_tau_rng'  :10e-9, # steps of 2e-9
									'C_N' 		: [62],#[36,44], # 34,
									'C_N_steps' : 12} # steps of 2 	


	qt.multi_tau_carbon_dict['C6'] = {'C_taus' 	: [9.248e-6],#[6.17e-6,9.355e-6,19.625e-6],#[17.175e-6, 19.395e-6, 23.838e-6 ,24.940e-6],
	 								'C_tau_rng' : 10e-9,
									'C_N' 		: [28], 
									'C_N_steps' : 12} 


	qt.multi_tau_carbon_dict['C7'] = {'C_taus' 	: [10.858e-6], #9.458e-6,11.682e-6,
	 								'C_tau_rng' : 10e-9,
									'C_N' 		: [44], #56,62,
									'C_N_steps' : 12} 

elif qt.current_setup == 'm1':
	qt.multi_tau_carbon_dict['C1'] = {'C_taus' 	: [7.216e-6], #9.458e-6,11.682e-6,
	 								'C_tau_rng' : 2e-9,
									'C_N' 		: [40], #56,62,
									'C_N_steps' : 6} 
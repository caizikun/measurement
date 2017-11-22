import qt
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

# Input parameters
name='ESR_SIL18_M1_LT'
print 'Please click `sequence` in run mode AWG!'

start_f 		= 1.746666 - 50e-3  #in GHz
stop_f  		= 1.746666 + 50e-3  #in GHz

# start_f 		= 4.009 - 50e-3  #in GHz
# stop_f  		= 4.009 + 50e-3  #in GHz

steps   		= 81
mw_power 		= -14. 			#in dBm (has been -3 for hans as well) 
green_power 	= 5e-6
int_time 		= 50       		#in ms
reps 			= 10			

#Generate list of frequencies
f_list = linspace(start_f*1e9, stop_f*1e9, steps)

ins_smb 	= qt.instruments['SGS100A_2']
ins_adwin 	= qt.instruments['adwin']
ins_counters= qt.instruments['counters']
ins_awg     = qt.instruments['AWG']

counter 	= 1
MW_power 	= mw_power

qt.instruments['GreenAOM'].set_power(green_power)
qt.msleep(20)

ins_counters.set_is_running(0)

# create data object
qt.mstart()

ins_awg.set_ch4_marker2_low(2)
ins_awg.set_ch4_status('On')
ins_smb.set_power(MW_power)
ins_smb.set_iq('off')
ins_smb.set_pulm('off')

ins_smb.set_status('on')
qt.msleep(0.2)

#ins_counters.set_is_running(0)
total_cnts = zeros(steps)
stop_scan=False
for cur_rep in range(reps):

    print 'sweep %d/%d ...' % (cur_rep+1, reps)

    for i,cur_f in enumerate(f_list):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        ins_smb.set_frequency(cur_f)

        qt.msleep(0.2)

        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name=name, clear=True)
    if stop_scan: break

x = f_list*1e-6
y = total_cnts
guess_width = 6 #0.2e-3
guess_amplitude = 1/2.0*(total_cnts[1]+total_cnts[-1])


total_cts_list = array(total_cnts)
val, idx = min((val, idx) for (idx, val) in enumerate(total_cts_list))

guess_ctr = f_list[idx]*1e-6

print guess_ctr

# x_axis = x*1e6

# fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, center_f,
#     guess_amplitude, guess_width, guess_ctr,
# #     # (2, guess_splitN), 
# #     # (2, guess_splitC),
# #     # (2, guess_splitB),
# #     #(3, guess_splitN), 
#     do_print=False, ret=True, do_plot = True, fixed=[4])

# fd = zeros(len(x_axis))  

# if type(fit_result) != type(False):
#     fd = fit_result['fitfunc'](x_axis*1e-6)
# else:
#     print 'could not fit curve!'

# d.add_data_point(f_list, total_cnts,fd)
# p_c = qt.Plot2D(d, 'bO-', coorddim=0, name=name, valdim=1, clear=True)
# p_c.add_data(d, coorddim=0, valdim=2)
# qt.msleep(0.15)
# p_c.save_png(filename+'.png')
# d.close_file()

# qt.mend()

# ins_counters.set_is_running(1)
# GreenAOM.set_power(2e-6)

# print fit_result['params_dict']['x0']

# f0[ii] = fit_result['params_dict']['x0']
# u_f0[ii] = fit_result['error_dict']['x0']



ins_smb.set_status('off')

d = qt.Data(name=name)
d.add_coordinate('frequency [GHz]')
d.add_value('counts')
d.create_file()
filename=d.get_filepath()[:-4]

d.add_data_point(f_list, total_cnts)
d.close_file()
p_c = qt.Plot2D(d, 'bO-', coorddim=0, name=name, valdim=1, clear=True)
p_c.save_png(filename+'.png')

qt.mend()

ins_counters.set_is_running(1)

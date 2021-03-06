import qt
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

name='ESR_111no2_SIL5_LT4'
start_f = 1.70#78 - 0.08 #   2.853 #2.85 #  #in GHz
stop_f  = 1.73#) + 0.08 #   2.864 #2.905 #   #in GHz
steps   = 101
mw_power = -14. #in dBm
green_power = 10e-6
int_time = 30       #in ms
reps = 20

#generate list of frequencies
f_list = linspace(start_f*1e9, stop_f*1e9, steps)

ins_smb = qt.instruments['SGS100']
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
counter = 1
MW_power = mw_power

ins_counters.set_is_running(0)

# create data object 
qt.mstart()

ins_smb.set_power(MW_power)
ins_smb.set_iq('off')
ins_smb.set_pulm('off')

ins_smb.set_status('on')

qt.msleep(0.2)
#ins_counters.set_is_running(0)
total_cnts = zeros(steps)
qt.instruments['GreenAOM'].set_power(green_power)
stop_scan=False
count =0 
for cur_rep in range(reps):
    
    print 'sweep %d/%d ...' % (cur_rep+1, reps)
    if count == 5:
    	optimiz0r.optimize(dims=['z','x','y'],int_time=50)
    	count = 0
    count+=1
    for i,cur_f in enumerate(f_list):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        ins_smb.set_frequency(cur_f)
        
        qt.msleep(0.05)

        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name=name, clear=True)
    if stop_scan: break
   
    

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

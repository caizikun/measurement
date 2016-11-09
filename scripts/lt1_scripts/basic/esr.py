import qt
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

name='Harry Scan 1 NV2'

start_f = 2.87 - 0.10#2.838-0.05#2.823#2.878 - 0.08 #   2.853 #2.85 #  #in GHz ZFS =2.878 "lt & RT"
stop_f  = 2.87 + 0.10#2.838+0.05#2.853#2.878 + 0.08 #   2.864 #2.905 #   #in GHz
steps = 201
f_list=np.linspace(start_f*1e9,stop_f*1e9,steps)
zoom_around_three_lines = False

mw_power = 15#in dBm
green_power = 200e-6
int_time = 30       #in ms
reps = 250

if zoom_around_three_lines:
	#For unequally spaced array
	Hf=2.19e-3 # in GHz
	fcntr=2.83573 # in GHz
	frange = 125e-6	# half of the freq range in GHz
	steps   = 21	# steps per line
	f_list_m1 = list(linspace((fcntr-Hf-frange)*1e9, (fcntr-Hf+frange)*1e9, steps))
	f_list_0 = list(linspace((fcntr-frange)*1e9, (fcntr+frange)*1e9, steps))
	f_list_p1 = list(linspace((fcntr+Hf-frange)*1e9, (fcntr+Hf+frange)*1e9, steps))

	f_list=np.array([(fcntr-Hf-frange-frange)*1e9]+f_list_m1+[(fcntr-Hf)*1e9/2.]+f_list_0+[(fcntr+Hf)*1e9/2.]+f_list_p1+[(fcntr+Hf+frange+frange)*1e9])

ins_smb = qt.instruments['SMB100']
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
counter = 2
MW_power = mw_power

ins_counters.set_is_running(1)

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

for cur_rep in range(reps):
    
    print 'sweep %d/%d ...' % (cur_rep+1, reps)
    
    for i,cur_f in enumerate(f_list):
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == 'q': 
                stop_scan=True
            elif ch == 'x':
                stop_scan=True
                break
            
        ins_smb.set_frequency(cur_f)
        
        
        qt.msleep(0.1)

        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        #total_cnts[i]+=ins_adwin.get_countrates()[counter-1]
        # qt.msleep(0.01)
    if stop_scan: break
    p_c = qt.Plot2D(f_list, total_cnts, 'bO-', name=name, clear=True)
    if cur_rep%5==0 and cur_rep!= 0:
        optimiz0r.optimize(dims=['x','y','z'], cycles = 1, int_time = 100, cnt=2)
        qt.msleep(1)
    
    
   
    

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
GreenAOM.turn_off()
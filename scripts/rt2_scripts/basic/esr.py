import qt
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence

name='Hillary_scan9_spot2'
start_f = 2.80 #-0.014 # #0.0#    2.853 #2.85 #  #in GHz
stop_f  = 2.88 #+0.014 # #0.05#   2.864 #2.905 #   #in GHz
steps   = 91
mw_power = 15 #in dBm
green_power = 50e-6 #20e-6
int_time = 50       #in ms
reps = 500

#generate list of frequencies
f_list = linspace(start_f*1e9, stop_f*1e9, steps)

ins_smb = qt.instruments['SMB100']
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
opt_ins = qt.instruments['optimiz0r']

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
for cur_rep in range(reps):
    
    print 'sweep %d/%d ...' % (cur_rep+1, reps)
    # optimiz0r.optimize(dims=['x','y','z','x','y'],int_time=50)
    for i,cur_f in enumerate(f_list):
        if msvcrt.kbhit():
            ch = msvcrt.getch() 
            if ch == 'q': 
                stop_scan=True
            elif ch == 'x':
                stop_scan=True
                break

        ins_smb.set_frequency(cur_f)
        
        qt.msleep(0.01)

        total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]
        # qt.msleep(0.01)

    p_c = qt.Plot2D(name=name, clear=True)
    p_c.add(f_list, total_cnts, 'bO',yerr = np.sqrt(total_cnts) )
    p_c.add(f_list, total_cnts, 'b-')

    
    if cur_rep%20 == 0 and cur_rep!=0:
        qt.msleep(2)
        opt_ins.optimize(dims=['x','y','z'], cycles=1)
        qt.msleep(2)





    if stop_scan: break
   
    

ins_smb.set_status('off')

d = qt.Data(name=name+'_esr')
d.add_coordinate('frequency [GHz]')
d.add_value('counts')
d.create_file()
filename=d.get_filepath()[:-4]

d.add_data_point(f_list, total_cnts)
d.close_file()
p_c = qt.Plot2D(name=name, clear=True)
p_c.add(f_list, total_cnts, 'bO',yerr = np.sqrt(total_cnts) )
p_c.add(f_list, total_cnts, 'b-')
p_c.save_png(filename+'.png')

qt.mend()

ins_counters.set_is_running(1)


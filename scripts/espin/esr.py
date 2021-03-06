import qt
import msvcrt
import numpy as np

SAMPLE = qt.exp_params['samples']['current']

##############
### Inputs ###
##############

name='ESR_'+ qt.exp_params['protocols']['current']

green_power = 20e-6     #15e-6
int_time    = 30     # in ms
reps        = 50

if False: #m1 transition
    range_f     =  0.01 # 0.03 in GHz
    steps       = 101      #101
    mw_power    = -20#-13      #in dBm
    center_f    =  1.705#4.055#3.95#1.74666#2.828#2.861
else: #p1 transition
    range_f     =  0.05 # 0.03 in GHz
    steps       = 101      #101
    mw_power    = -18     #in dBm
    center_f    = 4.06#25
#generate list of frequencies
f_list = np.linspace((center_f-range_f)*1e9, (center_f+range_f)*1e9, steps)

# Set source to use
#ins_smb = qt.instruments['SGS100']
ins_smb = qt.instruments['SMB100']
IQ_modulation = True #Does this source have IQ modulation?

# Set other instruments
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']
ins_awg = qt.instruments['AWG']

###############
### Run ESR ###
###############

counter = 1
MW_power = mw_power
ins_counters.set_is_running(0)
ins_awg.set_ch4_marker2_low(2)
ins_awg.set_ch4_status('On')

# create data object
qt.mstart()

if IQ_modulation:
    ins_smb.set_iq('off')

ins_smb.set_pulm('off')
ins_smb.set_power(MW_power)
ins_smb.set_status('on')

qt.msleep(0.2)
#ins_counters.set_is_running(0)
total_cnts = np.zeros(steps)
ins_aom.set_power(green_power)
stop_scan=False
optimizer_counter = 0
for cur_rep in range(reps):
    if optimizer_counter ==5:
        optimiz0r.optimize(dims=['z','x','y'],int_time=50)
        optimizer_counter = 0
    optimizer_counter +=1
    print 'sweep %d/%d ...' % (cur_rep+1, reps)
    for i,cur_f in enumerate(f_list):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        ins_smb.set_frequency(cur_f)
        qt.msleep(0.1)

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
ins_aom.turn_off()
import qt
import msvcrt
# from measurement.AWG_HW_sequencer_v2 import Sequence
import time
name='ESR_Donald_RT'
range_f = 50e-3
for centre_f in [2.7]:#,2.6,2.8,2.9,3.0]:
    start_f = centre_f - range_f #2.827 - 0.015 #   2.853 #2.85 #  #in GHz
    stop_f  = centre_f + range_f #2.827 + 0.015 #   2.864 #2.905 #   #in GHz
    steps   = 101
    mw_power = 19. #in dBm (has been -3 for hans as well)
    green_power = 300e-6
    int_time = 250       #in ms
    reps = 60

    #generate list of frequencies
    f_list = linspace(start_f*1e9, stop_f*1e9, steps)

    ins_smb = qt.instruments['SGS100A']
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
    qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x','z'])
    stop_scan=False
    stop_sweep=False
    for cur_rep in range(reps):

        print 'sweep %d/%d ...' % (cur_rep+1, reps)
        for i,cur_f in enumerate(f_list):
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
            ins_smb.set_frequency(cur_f)

            # qt.msleep(0.05)
            total_cnts[i]+=ins_adwin.measure_counts(int_time)[counter-1]

        # if cur_rep+1 % 30 == 0:
        #     qt.instruments['GreenAOM'].set_power(green_power)
        #     qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x'])


        p_c = qt.Plot2D(name=name, clear=True)
        p_c.add(f_list,total_cnts,'bO',yerr=np.sqrt(total_cnts))
        p_c.add(f_list,total_cnts,'b-')

        if stop_scan: break



    ins_smb.set_status('off')

    d = qt.Data(name=name)
    d.add_coordinate('frequency [GHz]')
    d.add_value('counts')
    d.add_value('errors')
    d.create_file()
    filename=d.get_filepath()[:-4]

    d.add_data_point(f_list, total_cnts,np.sqrt(total_cnts))
    d.close_file()
    p_c = qt.Plot2D(name=name,clear=True)
    p_c.add(f_list,total_cnts,'bO',yerr=np.sqrt(total_cnts))
    p_c.add(f_list,total_cnts,'b-')
    p_c.save_png(filename+'.png')

    qt.mend()

    ins_counters.set_is_running(1)

    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
    if stop_scan: break

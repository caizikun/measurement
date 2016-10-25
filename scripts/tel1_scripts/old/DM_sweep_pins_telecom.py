import time
import qt
import data
from analysis.lib.fitting import fit, common
from analysis.lib.tools import toolbox as tb
from numpy import *
import msvcrt
from instrument import Instrument
# current_adwin = qt.instruments['adwin']
counter=1 


def optimize_single_pin(pin_nr):
    #measurement parameters
    pin_nr=pin_nr
    name = 'DM_qTelecom_sweep_single_pin_nr_'+str(pin_nr)
    steps=11
    #cur_F=(okotech_dm.get_voltage(pin_nr)/2.)**2
    
    #F_min=cur_F-.2
    #F_max=cur_F+.2

    #v_min=0
    #v_max=2
    counter=1    #number of counter
    int_time=400 # in ms


    # powermeter = qt.instruments.get_instruments()['powermeter']
    # powermeter.set_wavelength (637e-9)
    powermeter = qt.instruments['powermeter_telecom']
    # powermeter.set_wavelength (637e-9)
    # current_mos = qt.instruments['master_of_space']
    # current_adwin = qt.instruments['adwin']
    DM=qt.instruments['okotech_dm']
    prev_value=DM.get_voltages()[pin_nr]  #XXXX[pin_nr-1]
    cur_F=(prev_value/2.)**2

    F_min=cur_F-.4
    F_max=cur_F+.4

    
    if F_min<0:
        F_min=0
    if F_max>1:
        F_max=1.4
    F = linspace(F_min,F_max,steps)

    y_NV = zeros(steps,dtype = float)


    br=False
    for i,force in enumerate(F):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            br = True
            break
        voltage=2*np.sqrt(force)    
        DM.set_voltage_single_pin(pin_nr,voltage)
        time.sleep(0.5)

        y_NV[i] = powermeter.get_power()*1e6
        print y_NV[i]
        # y_NV[i] = current_adwin.measure_counts(int_time)[counter-1]/(int_time*1e-3)

        #print 'step %s, counts %s'%(i,y_NV[i])
            
     
    x_axis = F

    dat = qt.Data(name='DM_sweep_curve_'+name)
    dat.create_file()
    dat.add_coordinate('Displacement [a.u.]')
    dat.add_value('DFG power [uW]')
    plt = qt.Plot2D(dat, 'ro', name='Optimization pin', coorddim=0, valdim=1, clear=True)
    plt.add_data(dat, coorddim=0, valdim=2)

    plt.set_plottitle(dat.get_time_name())
    dat.add_data_point(x_axis,y_NV)
    plt.set_legend(False)

    plt.save_png(dat.get_filepath()+'png')
    dat.close_file()

    highest_cntrate_idx=tb.nearest_idx(y_NV,y_NV.max())
    opt_V=2*np.sqrt(F[highest_cntrate_idx])
    DM.set_voltage_single_pin(pin_nr,opt_V)
    counters.set_is_running(True)


for j in np.arange(1):
    stop_scan=False
    print 'cur cycle = ' , j
    for i in np.arange(40):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        if (i!=2) and (i!=0):
            optimize_single_pin(i)
        else:
            print 'Dont optimize 2 or 0, those are ground/non existent '
        if stop_scan: break    
    if stop_scan: break


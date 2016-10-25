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
    steps=21
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
    prev_value= DM.get_voltage(pin_nr) #DM.get_voltages()[pin_nr-1]

    V_min= prev_value-.15
    V_max= prev_value+.15


    if V_min<0:
        V_min=0
    if V_max>2:
        V_max=2
    V = linspace(V_min,V_max,steps)

    y_Power = zeros(steps,dtype = float)

    print 'Optimization  pin number :', pin_nr
    print 'Voltage range : [', V_min, ';', V_max, ']'

    br=False
    for i,voltage in enumerate(V):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            br = True
            break  
        DM.set_voltage_single_pin(pin_nr,voltage)
        time.sleep(0.2)

        # y_Power[i] = powermeter.get_power()*1e6
        for k in range(5):
            y_Power[i] = y_Power[i] + powermeter.get_power()
            time.sleep(0.1)
        y_Power[i] = y_Power[i]*2e5
        #print y_Power[i]
        # y_NV[i] = current_adwin.measure_counts(int_time)[counter-1]/(int_time*1e-3)

        #print 'step %s, counts %s'%(i,y_NV[i])
            
     
    x_axis = V

    dat = qt.Data(name='DM_sweep_curve_'+name)
    dat.create_file()
    dat.add_coordinate('Pixel voltage [V]')
    dat.add_value('Power [uW]')
    plt = qt.Plot2D(dat, 'ro', name='Optimization pin', coorddim=0, valdim=1, clear=True)
    plt.add_data(dat, coorddim=0, valdim=2)

    plt.set_plottitle(dat.get_time_name())
    dat.add_data_point(x_axis,y_Power)
    plt.set_legend(False)

    plt.save_png(dat.get_filepath()+'png')
    dat.close_file()

    highest_cntrate_idx=tb.nearest_idx(y_Power,y_Power.max())
    opt_V=V[highest_cntrate_idx]
    DM.set_voltage_single_pin(pin_nr,opt_V)
    print 'Optimal voltage : ', opt_V, 'V' 
    print 'Highest power : ', y_Power.max(), 'uW \n'
    



for j in np.arange(3):
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


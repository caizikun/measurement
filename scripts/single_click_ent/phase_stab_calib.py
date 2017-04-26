import qt
import data
from analysis.lib.fitting import fit, common
from numpy import *
import msvcrt

#measurement parameters
name = 'PhaseMsmtCalibration'
steps=21
counter=1 #number of counter
Vmax = 0.1

phase_aom = qt.instruments['PhaseAOM']
current_adwin = qt.instruments['adwin']

dat = qt.Data(name='Saturation_curve_'+name)
dat.create_file()
dat.add_coordinate('Power [uW]')
dat.add_value('Counts [Hz]')
plt = qt.Plot2D(dat, 'rO', name='Saturation curve', coorddim=0, valdim=1, clear=True)
plt.add_data(dat, coorddim=0, valdim=2)
plt.set_plottitle(dat.get_time_name()+', Sat. cts: {:d}, sat. pwr: {:.2f} uW'.format(int(fitres['params_dict']['A']),fitres['params_dict']['xsat']))

plt.save_png(dat.get_filepath()+'png')
dat.close_file()

def measure_counts():

    phase_aom.set_power(0)
    qt.msleep(1)

    V_setpoint = -1

    print 'Calibrating PhaseAOM countrate'
    for v in linspace(0,Vmax,steps):
        phase_aom.apply_voltage(v)
        qt.msleep(0.2)
        counts = current_adwin.get_countrates()[counter-1]
        if (counts > 1e6):
            V_setpoint = v
            break

    phase_aom.set_power(0)

    return V_setpoint

def measure_interferometer():

    print 'Calibrating Interferometer'
    
    current_adwin.load_fibre_stretcher_setpoint()
    current_adwin.start_fibre_stretcher_setpoint(delay = 4)
    qt.msleep(10)
    current_adwin.stop_fibre_stretcher_setpoint()

    print 'Start Phase stability Calibration'
    self.measure_counts()
    self.measure_interferometer()
    g_0 = qt.instrument['physical_adwin'].Get_FPar(75)
    visibility = qt.instrument['physical_adwin'].Get_FPar(76)

    self.save_adwin_data(name,[ ('AOM_setpoint',1, self.V_setpoint),
                                ('g_0',1, g_0),
                                ('Visibility',1, visibility),
                                ])
    print 'Finished'

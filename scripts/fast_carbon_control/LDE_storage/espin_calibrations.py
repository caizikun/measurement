import numpy as np
import qt 
import measurement.scripts.espin.calibrate_mw_pulses as calibrate_mw_pulses
import measurement.scripts.ssro.ssro_calibration as ssro_calibration
import msvcrt
import datetime

from analysis.lib.tools import toolbox as tb
from analysis.lib.m2 import m2
from analysis.lib.m2.ssro import ssro as a_ssro
from analysis.lib.math import readout_correction as roc
from analysis.lib.math import error
from analysis.lib.fitting import fit, common
from analysis.lib.tools import plot
reload(m2)
reload(tb)
reload(a_ssro)

import measurement.scripts.carbonspin.write_to_msmt_params as write_to_msmt_params
reload(write_to_msmt_params)

execfile(qt.reload_current_setup)

SAMPLE_CFG = qt.exp_params['protocols']['current']
SAMPLE = qt.exp_params['samples']['current']
trans = qt.exp_params['samples'][SAMPLE]['electron_transition']
repeat_pi_msmt = 3
repeat_pi2_msmt = 3

### ssro calibration
print("[msmt] SSRO calibration")
stools.turn_off_all_lasers()
ssro_calibration.ssrocalibration(SAMPLE_CFG)

print("[analysis] SSRO calibration")
reload(a_ssro)
a_ssro.ssrocalib(contains = 'ROCali',plot_photon_ms0=False)

### mw pi calibration
reload(calibrate_mw_pulses)
from analysis.scripts.bell import calibration_tools
reload(calibration_tools)

pi_optima = []

for i in xrange(repeat_pi_msmt):
    print("[msmt] Pi calibration #%d" % i)
    calibrate_mw_pulses.calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity=11, debug=False, mw2=False)

    print("[analysis] Pi calibration #%d" % i)
    folder=tb.latest_data('Pi_Calibration')
    print folder
    # fig, ax = plt.subplots(1,1, figsize=(4.5,4))
    fit=calibration_tools.fit_parabolic(folder, x0_guess=0.88,a_guess=20,of_guess=0.06)#, info_xy=(0.88,ymin-(ymax-ymin)*0.35))
    print 'fitted infidelity', np.round(1-fit['params'][0],3)
    print 'Fitted minimum at ', np.round(fit['params'][2],3)

    pi_optima.append(np.round(fit['params'][2],3))

pi_optima = np.array(pi_optima)
avg_pi_optimum = np.mean(pi_optima)
print("Optima: " + str(pi_optima))
print("Average: %.3f" % avg_pi_optimum)

write_to_msmt_params.write_etrans_param_to_msmt_params_file(
    var_name="hermite_pi_amp",
    trans=trans,
    new_value="%.3f" % avg_pi_optimum,
    debug=False
)

### mw pi2 calibration
reload(calibrate_mw_pulses)
import analysis.scripts.espin.calibration_pi2_CORPSE as calibration_pi2_CORPSE
reload(calibration_pi2_CORPSE)
pi2_optima = []

for i in xrange(repeat_pi2_msmt):
    print("[msmt] Pi/2 calibration #%d" % i)
    calibrate_mw_pulses.calibrate_pi2_pulse(SAMPLE_CFG + 'Hermite_Pi2', debug = False, mw2=False)

    print("[analysis] Pi/2 calibration #%d" % i)
    fr = calibration_pi2_CORPSE.analyse_pi2_calibration()

    pi2_optima.append(fr['params_dict']['x0'])

pi2_optima = np.array(pi2_optima)
avg_pi2_optimum = np.mean(pi2_optima)
print("Optima: " + str(pi2_optima))
print("Average: %.3f" % avg_pi2_optimum)

write_to_msmt_params.write_etrans_param_to_msmt_params_file(
    var_name="hermite_pi2_amp",
    trans=trans,
    new_value="%.3f" % avg_pi2_optimum,
    debug=False
)

try:
    with open('espin_calibration_log.txt', 'a') as file:
        file.write("[%s]\n" % (str(datetime.datetime.now())))
        file.write("Pi calibration optima: " + str(pi_optima) + "\n")
        file.write("Updated pi pulse amplitude to: %.3f\n" % avg_pi_optimum)
        file.write("Pi/2 calibration optima: " + str(pi2_optima) + "\n")
        file.write("Updated pi/2 pulse amplitude to: %.3f\n" % avg_pi2_optimum)
        file.write("\n")
except:
    print("Writing to log file failed")
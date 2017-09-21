"""
Execute this script to reset the NV frequencies to its 0 voltage values
Works fine for Pippin SIL3 operated at 54.0 GHz
"""


import qt
# import numpy as np
import time

wait_time_for_green_reset = 20
green_power = 100e-6

ans = qt.instruments['purification_optimizer'].set_pid_e_primer_running(False)
if ans  : 
    print 'E_primer pid turned off'
else : 
    print 'ERROR : E_primer might still be running !!'

ans = qt.instruments['purification_optimizer'].set_pidgate_running(False)
if ans  : 
    print 'gate pid turned off'
else : 
    print 'ERROR : the gate pid might still be running !!'

ans = qt.instruments['purification_optimizer'].set_pidyellowfrq_running(False)
if ans : 
    print 'yellow pid turned off'
else : 
    print 'ERROR : the gate pid might still be running !!'

cur_gate_volt = qt.instruments['ivvi'].get_dac3()
#print 'current gate voltage is {:.2f} V'.format(cur_gate_volt)
qt.msleep(1)

ans = qt.instruments['ivvi'].set_dac3(0.0)
if ans : 
    print 'Gate dac3 set to 0.0 V'
else : 
    print 'ERROR : the gate voltage might not be 0V !!'

qt.msleep(5)

ans = qt.instruments['GreenServo'].move_out()
if ans  : 
    print 'Green Servo moved out'
else : 
    print 'ERROR with the Green Servo !!'



qt.instruments['GreenAOM'].set_power(green_power)


qt.instruments['adwin'].load_linescan()
qt.msleep(2)
optimiz0r.optimize(dims=['x','y'], cnt=1, cycles=5)
print 'Green AOM switched on for {} s at {:.0f} uW'.format(wait_time_for_green_reset,green_power*1e6)
qt.msleep(wait_time_for_green_reset)

qt.instruments['GreenAOM'].set_power(5e-6)
optimiz0r.optimize(dims=['x','y'], cnt=1, cycles=2)






ans = qt.instruments['GreenAOM'].set_power(0e-6) 
print 'Green AOM switched off'

print 'resetting Yellow and NewFocus to their default values'
# resetting yellow frequency
physical_adwin.Set_FPar(52,14.45)
qt.msleep(1)
# resetting newfocus frequency
physical_adwin.Set_FPar(51,43.75)
qt.msleep(1)

ans = qt.instruments['GreenServo'].move_in()
if ans  : 
    print 'Green Servo moved in'
else : 
    print 'ERROR with the Green Servo !!'

# ans1 = qt.instruments['purification_optimizer'].set_pid_e_primer_running(True)
# ans2 = qt.instruments['purification_optimizer'].set_pidgate_running(True)
# ans3 = qt.instruments['purification_optimizer'].set_pidyellowfrq_running(True)
# if ans1 & ans2 & ans3 : 
#     print 'The 3 pids are turned on again'
# else : 
#     print 'ERROR : check the pids !!'
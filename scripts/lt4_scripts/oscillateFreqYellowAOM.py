import msvcrt
for i in range(20000):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    adwin.set_dac_voltage(('yellow_aom_frq',5))
    qt.msleep(0.200)
    adwin.set_dac_voltage(('yellow_aom_frq',7.68))
    qt.msleep(0.200)
    adwin.set_dac_voltage(('yellow_aom_frq',9))
    qt.msleep(0.200)
  
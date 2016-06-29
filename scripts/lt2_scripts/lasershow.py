import msvcrt
for i in range(20000):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    GreenAOM.apply_voltage(GreenAOM.get_V_max())
    # YellowAOM.apply_voltage(0)
    qt.msleep(0.1)
    MatisseAOM.apply_voltage(MatisseAOM.get_V_max())
    qt.msleep(0.1)
    GreenAOM.set_power(0)
    qt.msleep(0.1)
    NewfocusAOM.apply_voltage(NewfocusAOM.get_V_min())
    qt.msleep(0.1)
    MatisseAOM.set_power(0)
    qt.msleep(0.1)
    NewfocusAOM.apply_voltage(0)
    qt.msleep(0.1)
    #YellowAOM.apply_voltage(YellowAOM.get_V_max())
    # YellowAOM.turn_on()
    qt.msleep(0.2)
     

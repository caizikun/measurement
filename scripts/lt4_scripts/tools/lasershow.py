import msvcrt
for i in range(100000):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    PulseAOM.turn_on()
    MatisseAOM.turn_on()
    NewfocusAOM.turn_on()
    GreenAOM.turn_on()
    YellowAOM.turn_on()
    qt.msleep(0.4)
    PulseAOM.turn_off()
    MatisseAOM.turn_off()
    NewfocusAOM.turn_off()
    GreenAOM.turn_off()
    YellowAOM.turn_off()
    qt.msleep(0.4)
     

import msvcrt
for i in range(20000):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    speed=0.02
    GreenAOM.turn_on()
    qt.msleep(np.random.randint(1,10)*speed)
    MatisseAOM.turn_on()
    qt.msleep(np.random.randint(1,10)*speed)
    GreenAOM.turn_off()
    qt.msleep(np.random.randint(1,10)*speed)
    NewfocusAOM.turn_on()
    qt.msleep(np.random.randint(1,10)*speed)
    MatisseAOM.turn_off()
    qt.msleep(np.random.randint(1,10)*speed)
    NewfocusAOM.turn_on()
    qt.msleep(np.random.randint(1,10)*speed)
    YellowAOM.turn_on()
    qt.msleep(np.random.randint(1,10)*speed)
    YellowAOM.turn_off()
    NewfocusAOM.turn_off()
     

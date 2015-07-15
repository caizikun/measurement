import qt
import msvcrt

def qstop(sleep=2):
    print '--------------------------------'
    print '---------- IN QUEUE! -----------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True


if qstop(sleep=5):
    print '--------------------------------'
    print 'Finished without executing queue'
    print '--------------------------------'
else:
    execfile(r'D:\measuring\measurement\scripts\QEC\NuclearT1_2.py')
    #execfile(r'D:\measuring\measurement\scripts\QEC\1Carbon_XY4.py')

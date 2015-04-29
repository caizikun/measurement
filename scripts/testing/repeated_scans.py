import msvcrt
i=0
while 1:
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
	if not(qt.instruments['linescan_counts'].get_is_running()):
		i+=1
	else:
		i=0
	if i >2:
		qt.instruments['scan2d'].set_is_running(True)
	qt.msleep(1)

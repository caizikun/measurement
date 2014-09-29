import msvcrt

def wait_a_minute():
    for i in range(6):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
			return False
		qt.msleep(10) 
    return True
breakd = False
for i in range(20):
	if breakd:
		break
	physical_adwin.Set_Par(59,1)
	qt.msleep(20)
	physical_adwin.Set_Par(59,0)
	for j in range(30):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): 
			breakd = True
			break
		if not wait_a_minute():
			breakd = True
			break



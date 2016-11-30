for i in np.arange(41):
	print i
	sleep(1)
	dac_list=[0]*40
	dac_list[i]=65535
	edac40.set_all(0,dac_list)
	if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break

	
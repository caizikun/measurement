cur_voltage = 2.5
step_size = 0.02
while True:
	adwin.set_dac_voltage(('delay_voltage', cur_voltage))
	print("Current voltage: %.2f" % cur_voltage)
	next_input = raw_input()
	if (next_input == "q"):
		break
	elif (next_input == "+"):
		cur_voltage += step_size
	elif (next_input == "-"):
		cur_voltage -= step_size
	else:
		try:
			cur_voltage = float(next_input)
		except:
			pass
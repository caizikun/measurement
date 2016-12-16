execfile(qt.reload_current_setup)
import msvcrt, time
import numpy as np
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

p_start = pulse.SquarePulse('sync1', length=100e-9, amplitude = 1)
p_stop = pulse.SquarePulse('p7889_stop', length=100e-9, amplitude = 1)
p_wait_length=10e-6
p_wait = pulse.SquarePulse('sync1', length=p_wait_length, amplitude = 0)
p_sync = pulse.SquarePulse('sync0', length=100e-9, amplitude = 1)

int_time = 10e-3 #s
wait_time = 1e-3 #s
reprate = 100e3 #KHz
pulse_reps = int_time*reprate
wait_reps = int(np.round(wait_time/p_wait_length))
elts = []

ypts=121

s= pulsar.Sequence('test_p7889_seq')
#for i in np.arange(y_pts):
e_sync=element.Element('sync_p7889_elt', pulsar=qt.pulsar)
e_sync.add(p_sync, start = 200e-9)
e_sync.add(p_wait)
e_wait=element.Element('wait_p7889_elt', pulsar=qt.pulsar)
e_wait.add(p_wait)
e=element.Element('p7889_elt', pulsar=qt.pulsar)
e.add(pulse.cp(p_wait,length = 1./reprate))
e.add(p_start, start=200e-9, name='start')
#e.add(p_stop, start=1e-9,   refpulse='start')
#e.add(p_stop, start=100e-9, refpulse='start')
#e.add(p_stop, start=300e-9, refpulse = 'start')
#e.append(T)

#for i in range(int_time*reprate):
	

#e.add(p_stop, start=30e-9*i,  refpulse = 'start')
#if i%2 == 0:
#		e.add(p_stop, start=100e-9, refpulse = 'start')


elts.append(e)
elts.append(e_wait)
elts.append(e_sync)

for i in range(ypts):
	s.append(name = 'sync_init'+str(i),
	                wfname = e_sync.name,
	                trigger_wait = 1,
	                repetitions = 1)
	s.append(name = 'wait'+str(i),
	                wfname = e_wait.name,
	                trigger_wait = 0,
	                repetitions = wait_reps)

	s.append(name = 'pulse'+str(i),
	                wfname = e.name,
	                trigger_wait = 0,
	                repetitions = pulse_reps)

#qt.pulsar.upload(*elts)
##qt.pulsar.program_sequence(s)
qt.pulsar.program_awg(s,*elts)



# qt.instruments['p7889'].set_number_of_cycles(ypts)
# qt.instruments['p7889'].set_number_of_sequences(1)
# qt.instruments['p7889'].set_sweepmode_sequential(True)
# qt.instruments['p7889'].set_sweep_preset(True)
# qt.instruments['p7889'].set_sweep_preset_number(pulse_reps)

# qt.instruments['p7889'].Start()
# qt.msleep(0.5)
qt.instruments['AWG'].start()

# t0 = time.time()
# c0 = 0
# p=np.zeros(100000,dtype = 'int')
# ii=0
# while qt.instruments['p7889'].get_state(): 
#     #time.sleep(0.1)
#     qt.msleep(0.2)
#     if msvcrt.kbhit():
#         kb_char=msvcrt.getch()
#         if kb_char == "q": 
#             stop = True
#             break
#     t1 = time.time()
#     c1 = qt.instruments['p7889'].get_RoiSum()
#     #p[min([int((c1-c0)/(t1-t0)),100000-1])]+=1
#     if ii%10 == 0:
#     	print (c1-c0)/(t1-t0)
#     t0 = t1
#     c0 = c1
#     ii+=1

# qt.instruments['p7889'].Stop()
# qt.msleep(0.5)
#qt.instruments['AWG'].stop()
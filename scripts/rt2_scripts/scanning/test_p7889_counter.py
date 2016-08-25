execfile(qt.reload_current_setup)
import msvcrt, time
import numpy as np
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

p_start = pulse.SquarePulse('p7889_start', length=10e-9, amplitude = 1)
p_stop = pulse.SquarePulse('p7889_stop', length=10e-9, amplitude = 1)
p_wait = pulse.SquarePulse('p7889_start', length=100e-6, amplitude = 0)

e=element.Element('test_p7889_elt', pulsar=qt.pulsar)
#e.append(T)
e.add(p_start, start = 100e-9, name = 'start')
e.add(p_stop, start=1e-9,   refpulse = 'start')
e.add(p_stop, start=30e-9,  refpulse = 'start')
e.add(p_stop, start=100e-9, refpulse = 'start')
e.append(p_wait)

e.print_overview()

s= pulsar.Sequence('test_p7889_seq')
s.append(name = 'test_p7889_seq_1',
                wfname = e.name,
                trigger_wait = 0)
qt.pulsar.upload(e)
qt.pulsar.program_sequence(s)



qt.instruments['p7889'].Start()
qt.msleep(0.5)
qt.instruments['AWG'].start()

t0 = time.time()
c0 = 0
p=np.zeros(100000,dtype = 'int')
ii=0
while qt.instruments['p7889'].get_state(): 
    #time.sleep(0.1)
    qt.msleep(0.2)
    if msvcrt.kbhit():
        kb_char=msvcrt.getch()
        if kb_char == "q": 
            stop = True
            break
    t1 = time.time()
    c1 = qt.instruments['p7889'].get_RoiSum()
    #p[min([int((c1-c0)/(t1-t0)),100000-1])]+=1
    if ii%10 == 0:
    	print (c1-c0)/(t1-t0)
    t0 = t1
    c0 = c1
    ii+=1

qt.instruments['p7889'].Stop()
qt.msleep(0.5)
qt.instruments['AWG'].stop()
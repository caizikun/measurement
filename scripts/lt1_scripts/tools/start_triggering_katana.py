import qt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

awg = qt.instruments['AWG']
pts=1#self._pixel_pts

p_wait = pulse.SquarePulse('sync', length=10e-6, amplitude = 0)
p_sync = pulse.SquarePulse('sync', length=200e-9, amplitude = 1)
elts=[]
s= pulsar.Sequence('test_flim_seq')
e=element.Element('sync_elt', pulsar=qt.pulsar)
e.add(p_sync, start = 200e-9)
e.add(p_wait)
elts.append(e)
for i in range(pts):
    s.append(name = 'sync_init'+str(i),
                    wfname = e.name,
                    trigger_wait = 0,
                    repetitions = 1)
qt.pulsar.program_awg(s,e)

# awg.start()
# i=0
# awg_ready = False
# while not awg_ready and i<100:
#     if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
#         raise Exception('User abort while waiting for AWG')
#     try:
#         if awg.get_state() == 'Waiting for trigger':
#             qt.msleep(1)
#             awg_ready = True
#             print 'AWG Ready!'
#             break
#         else:
#             print 'AWG not in wait for trigger state but in state:', awg.get_state()
#     except:
#         print 'waiting for awg: usually means awg is still busy and doesnt respond'
#         print 'waiting', i, '/ 100'
#         awg.clear_visa()
#         i=i+1

#     qt.msleep(0.5)
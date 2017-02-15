import qt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

awg = qt.instruments['AWG']
pts=1#self._pixel_pts
p_wait = pulse.SquarePulse('katana_trg', length=2e-6, amplitude = 0)
p_sync = pulse.SquarePulse('katana_trg', length=200e-9, amplitude = 1)
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
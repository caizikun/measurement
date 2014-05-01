import qt
execfile(qt.reload_current_setup)
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.pq import pq_measurement

def test_PQ_measurement(name):
    upload=False
    if upload:
        generate_test_sequence()
    m = pq_measurement.PQMeasurement(name)
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION
    m.params['MIN_SYNC_BIN']        =   0 
    m.params['MAX_SYNC_BIN']        =   1000 
    m.params['measurement_time']    =   1200 #sec
    m.params['measurement_abort_check_interval']    = 1. #sec

    m.run()
    m.finish()

def test_PQ_measurement_integrated(name):
    
    m = pq_measurement.PQMeasurementIntegrated(name)
    m.params['pts']                 =   10
    m.params['syncs_per_sweep']     =   10
    upload=True
    if upload:
        generate_sweep_test_sequence(m.params['pts'], m.params['syncs_per_sweep'] )
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION
    m.params['MIN_SYNC_BIN']        =   0 
    m.params['MAX_SYNC_BIN']        =   1000 
    m.params['measurement_time']    =   1200 #sec
    m.params['measurement_abort_check_interval']    = 1. #sec

    m.run()
    m.finish()
def generate_sweep_test_sequence(pts, syncs_per_sweep):
    sync = pulse.SquarePulse(channel = 'sync',
            length = 50e-9, amplitude = 2)
    sync_T = pulse.SquarePulse(channel = 'sync',
        length = 1e-6, amplitude = 0)

    ch0 = pulse.SquarePulse(channel = 'AOM_Yellow',
        length = 50e-9, amplitude = 2)
    #photon_T = pulse.SquarePulse(channel = 'AOM_Yellow',
    #    length = 1e-6, amplitude = 0)

    ch1 = pulse.SquarePulse(channel = 'RND_halt',
        length = 50e-9, amplitude = 2)
    #MA1_T = pulse.SquarePulse(channel = 'RND_halt',
    #    length = 1e-6, amplitude = 0)
    seq = pulsar.Sequence('PQ_testing')
    elts=[]
    for i in range(pts):
        elt = element.Element('el-{}'.format(i), pulsar=qt.pulsar)
        elt.add(sync_T,
            name='sync_T')
        elt.add(sync,
            refpulse='sync_T',
            name='sync')
        elt.add(ch0,
            start = 500e-9+i*10e-9,
            refpulse = 'sync',
            refpoint = 'start')
        elt.add(ch1,
            start = 250e-9+i*10e-9,
            refpulse = 'sync',
            refpoint = 'start')
    #elt.append(pulse.cp(photon_T, length=1e-6))

    #syncs_elt_mod0 = element.Element('2_syncs_photon_after_first', pulsar=qt.pulsar)
    #syncs_elt_mod0.append(sync_T)
    #s1 = syncs_elt_mod0.append(sync)
    #syncs_elt_mod0.append(pulse.cp(sync_T, length=500e-9))
    #s2 = syncs_elt_mod0.append(sync)
    #syncs_elt_mod0.append(pulse.cp(sync_T, length=10e-6))
    #syncs_elt_mod0.add(photon,
    #    start = 50e-9,
    #    refpulse = s1)

        elts.append(elt)
        seq.append(name = 'test-{}'.format(i),
            wfname = elt.name,
            repetitions = syncs_per_sweep,
            trigger_wait = True if i == 0 else False)
    #seq.append(name = 'photon_after_sync1',
    #    wfname = syncs_elt_mod0.name,
    #    repetitions = 100)

    #qt.pulsar.upload(no_syncs_elt, syncs_elt_mod0)
    #qt.pulsar.program_sequence(seq)
    qt.pulsar.program_awg(seq,*elts)
    #self.AWG.set_runmode('SEQ')
    #self.AWG.start()


def generate_test_sequence():
    sync = pulse.SquarePulse(channel = 'sync',
        length = 50e-9, amplitude = 2)
    sync_T = pulse.SquarePulse(channel = 'sync',
        length = 1e-6, amplitude = 0)

    ch0 = pulse.SquarePulse(channel = 'AOM_Yellow',
        length = 50e-9, amplitude = 2)
    #photon_T = pulse.SquarePulse(channel = 'AOM_Yellow',
    #    length = 1e-6, amplitude = 0)

    ch1 = pulse.SquarePulse(channel = 'RND_halt',
        length = 50e-9, amplitude = 2)
    #MA1_T = pulse.SquarePulse(channel = 'RND_halt',
    #    length = 1e-6, amplitude = 0)

    elt = element.Element('photon_without_sync', pulsar=qt.pulsar)
    elt.add(sync_T,
        name='sync_T')
    elt.add(sync,
        refpulse='sync_T',
        name='sync')
    elt.add(ch0,
        start = 500e-9,
        refpulse = 'sync',
        refpoint = 'start')
    elt.add(ch1,
        start = 250e-9,
        refpulse = 'sync',
        refpoint = 'start')
    #elt.append(pulse.cp(photon_T, length=1e-6))

    #syncs_elt_mod0 = element.Element('2_syncs_photon_after_first', pulsar=qt.pulsar)
    #syncs_elt_mod0.append(sync_T)
    #s1 = syncs_elt_mod0.append(sync)
    #syncs_elt_mod0.append(pulse.cp(sync_T, length=500e-9))
    #s2 = syncs_elt_mod0.append(sync)
    #syncs_elt_mod0.append(pulse.cp(sync_T, length=10e-6))
    #syncs_elt_mod0.add(photon,
    #    start = 50e-9,
    #    refpulse = s1)

    seq = pulsar.Sequence('PQ_testing')
    seq.append(name = 'test1',
        wfname = elt.name,
        repetitions = 1000,
        trigger_wait = True)
    #seq.append(name = 'photon_after_sync1',
    #    wfname = syncs_elt_mod0.name,
    #    repetitions = 100)

    #qt.pulsar.upload(no_syncs_elt, syncs_elt_mod0)
    #qt.pulsar.program_sequence(seq)
    qt.pulsar.program_awg(seq,elt)
    #self.AWG.set_runmode('SEQ')
    #self.AWG.start()


if __name__ == '__main__':
    test_PQ_measurement_integrated('test')
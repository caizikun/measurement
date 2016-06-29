import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq


class QRND(pq.PQMeasurement):

    mprefix = 'Bell_QRND'

    def generate_sequence(self):
        #p=pulse.SinePulse(channel='EOM_Matisse', name='pp', length=100e-6, frequency=1/(100e-6), amplitude = 1.8)
        sync = pulse.SquarePulse('sync', length=300e-9, amplitude = 1)
        T = pulse.SquarePulse('sync', length=1e-6, amplitude = 0)
        RND_halt = pulse.SquarePulse('RND_halt', length=200e-9, amplitude = 1)

        e=element.Element('Generate RND', pulsar=qt.pulsar)
        e.append(T)
        e.append(sync)
        e.append(T)
        e.append(RND_halt)
        e.append(T)
        e_wait = element.Element('Wait', pulsar=qt.pulsar)
        e_wait.append(pulse.cp(T, length = 10e-6))

        #e.print_overview()
        
        s= pulsar.Sequence('Generate QRND')
        s.append(name = 't1',
                        wfname = e.name,
                        trigger_wait = 0)
        s.append(name = 'wait',
                 wfname = e_wait.name,
                 repetitions = 100,
                 trigger_wait = 0)
        qt.pulsar.upload(e,e_wait)
        qt.pulsar.program_sequence(s)

    def start_measurement_process(self):
        qt.instruments['AWG'].start()
    def stop_measurement_process(self):
        qt.instruments['AWG'].stop()

    def finish(self):
        self.save_instrument_settings_file()
        self.save_params()
        pq.PQMeasurement.finish(self)

def generate_rnd(name):
    m = QRND(name)
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   8  #2**BINSIZE*BASERESOLUTION = 1 ps for HH
    m.params['MIN_SYNC_BIN']        =   0 #5 us 
    m.params['MAX_SYNC_BIN']        =   2000 #15 us 
    m.params['measurement_time']    =   100 #sec = 24H
    m.params['measurement_abort_check_interval']    = 1 #sec
    m.params['TTTR_read_count'] = 1000

    m.generate_sequence()
    m.run(debug=False)
    m.finish()

if __name__ == '__main__':
    generate_rnd('test-1')
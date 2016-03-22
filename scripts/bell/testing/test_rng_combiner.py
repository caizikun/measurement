import qt
import numpy as np
#execfile(qt.reload_current_setup)
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.pq import pq_measurement
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import time
import msvcrt




def test_run():
    
    PQ_ins = qt.instruments['HH_400']
    AWG = qt.instruments['AWG']
    rng_sender = qt.instruments['RND_bit_sender']
    if PQ_ins.OpenDevice():
        PQ_ins.start_T2_mode()
        if hasattr(PQ_ins,'calibrate'):
            PQ_ins.calibrate()
            PQ_ins.set_Binning(8)
    else:
        raise(Exception('Picoquant instrument '+PQ_ins.get_name()+ ' cannot be opened: Close the gui?'))


    target_n = 10e8
    pts = int(target_n/50000)
    print 'expected time:', pts/60., 'minutes'

    MIN_SYNC_BIN = np.uint64(0)
    MAX_SYNC_BIN = np.uint64(int(15e-6*1e12))
    MIN_HIST_SYNC_BIN = np.uint64(0)
    MAX_HIST_SYNC_BIN = np.uint64(int(18.5e-6*1e12))
    hist_length = np.uint64(MAX_HIST_SYNC_BIN- MIN_HIST_SYNC_BIN)
    hist = np.zeros((hist_length,2), dtype='u4')

    count_marker_channel = 1
    T2_READMAX = PQ_ins.get_T2_READMAX()
    TTTR_read_count = T2_READMAX
    TTTR_RepetitiveReadouts = 2
    T2_WRAPAROUND = np.uint64(PQ_ins.get_T2_WRAPAROUND())
    T2_TIMEFACTOR = np.uint64(PQ_ins.get_T2_TIMEFACTOR())

    t_lastsync = 0
    t_ofl = 0
    last_sync_number = 0
    
    PQ_ins.StartMeas(int(pts * 1e3*2)) # this is in ms

    n=0
    n0=0
    n1=0
    ne=0
    
    for i in range(pts):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
        if i%10==0 and n>0:
            print '{:.2f}%'.format(float(i)/pts*100),ne,'{:.2f}'.format(float(n0)/n)


        rnd_bits=np.random.randint(0,2,8)
        rnd_word='{:d}{:d}{:d}{:d}{:d}{:d}{:d}{:d}'.format(*rnd_bits)
        expected_parity = (np.sum(rnd_bits)+1)%2

        rng_sender.set_state_bitstring(rnd_word)
        qt.msleep(0.1,exact=True)
        AWG.force_trigger()
        qt.msleep(0.9, exact=True)
        
        _length = 0
        _data = np.array([],dtype = 'uint32')
        for j in range(TTTR_RepetitiveReadouts):
            cur_length, cur_data = PQ_ins.get_TTTR_Data(count = TTTR_read_count)
            _length += cur_length 
            _data = np.hstack((_data,cur_data[:cur_length]))

        if PQ_ins.get_Flag_FifoFull():
            print 'Aborting the measurement: Fifo full!'
            break
        if PQ_ins.get_Flag_Overflow():
            print 'Aborting the measurement: OverflowFlag is high.'
            break 
        if PQ_ins.get_Flag_SyncLost():
            print 'Aborting the measurement: SyncLost flag is high.'
            break
        _t, _c, _s = pq_measurement.PQ_decode(_data[:_length])

        hhtime, hhchannel, hhspecial, sync_time, hist, sync_number, \
                newlength, t_ofl, t_lastsync, last_sync_number, counted_markers = \
                T2_tools_v3.T2_live_filter(_t, _c, _s, hist, t_ofl, t_lastsync, last_sync_number,
                MIN_SYNC_BIN, MAX_SYNC_BIN, MIN_HIST_SYNC_BIN, MAX_HIST_SYNC_BIN, T2_WRAPAROUND,T2_TIMEFACTOR,count_marker_channel)
        
        
        if len(hhchannel)!= 100000:
            print 'error in HH set'
            break
        bits_qrng = hhchannel[(hhspecial==0)]
        bits_combiner = (hhchannel[(hhspecial==1)]/4)-1
        bits_combiner_expected = (bits_combiner+expected_parity)%2
        noof_errors = np.sum((bits_qrng+bits_combiner_expected)%2)
        #print np.array_equal(bits_qrng,bits_combiner)
        #print np.array_equal(bits_qrng,bits_combiner_expected)
        
        #print bits_qrng
        #print bits_combiner
        #print bits_combiner_expected
        #print last_sync_number,len(hhchannel)  
        n0+= np.sum((hhspecial==0)&(hhchannel==0))
        n1+= np.sum((hhspecial==0)&(hhchannel==1))
        n+=50000
        ne+=noof_errors
        #print np.sum((hhspecial==1)&(hhchannel==4)),np.sum((hhspecial==1)&(hhchannel==8))
        #print np.sum((hhspecial==1)&(hhchannel==4*(expected_parity+1)))        
        if not(np.sum((hhspecial==1)&(hhchannel==4*((expected_parity+1)%2+1))) == np.sum((hhspecial==0)&(hhchannel==1))):
            print 'found summing error', noof_errors
        #last_sync_number = 0      
    PQ_ins.StopMeas()   
    print n0, n1, n, ne
    return n0, n1, n, ne
    

def generate_test_sequence():

    RND_halt_combiner_ch = 'RND_halt'
    RND_halt_QRNG_ch = 'plu_sync'
    sync_ch = 'adwin_success_trigger'

    sync = pulse.SquarePulse(channel = sync_ch,
        length = 50e-9, amplitude = 2)
    RND_halt_QRNG = pulse.SquarePulse(channel = RND_halt_QRNG_ch,
        length = 200e-9, amplitude = 2)
    RND_halt_combiner = pulse.SquarePulse(channel = RND_halt_combiner_ch,
        length = 200e-9, amplitude = 2)

    elt = element.Element('combiner_test_elt', pulsar=qt.pulsar)
    elt.add(sync,
        name='sync_T',
        start = 100e-9)
    elt.add(RND_halt_QRNG,
        start = 500e-9,
        refpulse='sync_T',
        name='RND_halt_QRNG_p')
    elt.add(RND_halt_combiner,
        start = 100e-9,
        refpulse = 'RND_halt_QRNG_p',
        refpoint = 'start',
        name='RND_halt_combiner_p')
    elt.add(pulse.cp(sync, amplitude=0,length=15e-6))
    
    elt2 = element.Element('combiner_test_wait_elt', pulsar=qt.pulsar)

    elt2.add(pulse.cp(sync, amplitude=0,length=15e-6),
        start = 500e-9)

    seq = pulsar.Sequence('combiner_test_seq')

    seq.append(name = 'combiner_test_seq1',
        wfname = elt2.name,
        repetitions = 1,
        trigger_wait = True)
    seq.append(name = 'combiner_test_seq2',
        wfname = elt.name,
        repetitions = 50000,
        trigger_wait = False)

    #seq.append(name = 'photon_after_sync1',
    #    wfname = syncs_elt_mod0.name,
    #    repetitions = 100)

    #qt.pulsar.upload(no_syncs_elt, syncs_elt_mod0)
    #qt.pulsar.program_sequence(seq)
    qt.pulsar.program_awg(seq,elt,elt2)

def wait_for_awg(awg):
    awg_ready = False
    i=0
    while not awg_ready and i<100:
        #print '( not awg_ready and i < 100 ) == True'
        #print 'awg state: '+str(self.awg.get_state())

        if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
            raise Exception('User abort while waiting for AWG')

        try:
            if awg.get_state() == 'Waiting for trigger':
                qt.msleep(1)
                awg_ready = True
                print 'AWG Ready!'
            else:
                print 'AWG not in wait for trigger state but in state:', self.awg.get_state()
        except:
            print 'waiting for awg: usually means awg is still busy and doesnt respond'
            print 'waiting', i, '/ 100'
            awg.clear_visa()
            i=i+1

        qt.msleep(0.5)

if __name__ == '__main__':
    upload=True

    if upload:
        qt.instruments['AWG'].stop()
        generate_test_sequence()
        
        qt.instruments['AWG'].start()
        qt.msleep(0.2)
        wait_for_awg(qt.instruments['AWG'])
    n0, n1, n, ne=test_run()
    
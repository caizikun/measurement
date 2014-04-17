import struct
import numpy as np
from time import sleep, time, localtime
import datetime
import qt

from cStringIO import StringIO

class AWG5014_instrument:

    def pack_waveform(self,wf,m1,m2):
        '''
        packs analog waveform in 14 bit integer, and two bits for m1 and m2 in a single 16 bit integer
        '''
        wflen = len(wf)
        packed_wf = np.zeros(wflen,dtype=np.uint16)
        packed_wf +=wf*8191+8191+16384*m1+32768*m2
        return packed_wf

    def generate_awg_file(self,packed_waveforms,wfname_l, nrep, trig_wait, goto_state, jump_to, clock):
        '''
        packed_waveforms: dictionary containing packed waveforms with keys wfname_l and delay_labs
        wfname_l: array of waveform names array([[segm1_ch1,segm2_ch1..],[segm1_ch2,segm2_ch2..],...])
        nrep_l: list of len(segments) specifying the no of reps per segment (0,65536)
        wait_l: list of len(segments) specifying triger wait state (0,1)
        goto_l: list of len(segments) specifying goto state (0,65536, 0 means next)
        logic_jump_l: list of len(segments) specifying logic jump (0 = off)

        filestructure:
        if True:
            MAGIC
            VERSION
            SAMPLING_RATE
            RUN_MODE
            RUN_STATE
            CHANNEL_STATE_1
            CHANNEL_STATE_2
            CHANNEL_STATE_3
            CHANNEL_STATE_4

            WAVEFORM_NAME_N
            WAVEFORM_TYPE_N
            WAVEFORM_LENGTH_N
            WAVEFORM_TIMESTAMP_N
            WAVEFORM_DATA_N

            SEQUENCE_WAIT_M
            SEQUENCE_LOOP_M
            SEQUENCE_JUMP_M
            SEQUENCE_GOTO_M
            SEQUENCE_WAVEFORM_NAME_CH_1_M
            SEQUENCE_WAVEFORM_NAME_CH_2_M
            SEQUENCE_WAVEFORM_NAME_CH_3_M
            SEQUENCE_WAVEFORM_NAME_CH_4_M
        '''
        wfname_l
        timetuple = tuple(np.array(localtime())[[0,1,8,2,3,4,5,6,7]])
        timestamp = struct.pack('8h',*timetuple[:-1])
        chstate = []
        for wfch in wfname_l[0]:
            if wfch is None:
                chstate+=[0]
            else:
                chstate+=[0]
        head = self._pack_record('MAGIC',5000,'h')+\
                    self._pack_record('VERSION',1,'h')+\
                    self._pack_record('SAMPLING_RATE',clock,'d')+\
                    self._pack_record('REFERENCE_SOURCE',1,'h')+\
                    self._pack_record('TRIGGER_INPUT_THRESHOLD',1.0,'d')+\
                    self._pack_record('RUN_MODE',4,'h')+\
                    self._pack_record('RUN_STATE',0,'h')+\
                    self._pack_record('CHANNEL_STATE_1',1,'h')+\
                    self._pack_record('MARKER1_METHOD_1',2,'h')+\
                    self._pack_record('MARKER2_METHOD_1',2,'h')+\
                    self._pack_record('CHANNEL_STATE_2',1,'h')+\
                    self._pack_record('MARKER1_METHOD_2',2,'h')+\
                    self._pack_record('MARKER2_METHOD_2',2,'h')+\
                    self._pack_record('CHANNEL_STATE_3',1,'h')+\
                    self._pack_record('MARKER1_METHOD_3',2,'h')+\
                    self._pack_record('MARKER2_METHOD_3',2,'h')+\
                    self._pack_record('CHANNEL_STATE_4',1,'h')+\
                    self._pack_record('MARKER1_METHOD_4',2,'h')+\
                    self._pack_record('MARKER2_METHOD_4',2,'h')

        ii=21
        record_str = StringIO()

        wlist = packed_waveforms.keys()
        wlist.sort()
        for wf in wlist:
            wfdat = packed_waveforms[wf]
            lenwfdat = len(wfdat)
            #print 'WAVEFORM_NAME_%s: '%ii, wf, 'len: ',len(wfdat)
            record_str.write(self._pack_record('WAVEFORM_NAME_%s'%ii, wf+'\x00','%ss'%len(wf+'\x00'))+\
                        self._pack_record('WAVEFORM_TYPE_%s'%ii, 1,'h')+\
                        self._pack_record('WAVEFORM_LENGTH_%s'%ii,lenwfdat,'l')+\
                        self._pack_record('WAVEFORM_TIMESTAMP_%s'%ii, timetuple[:-1],'8H')+\
                        self._pack_record('WAVEFORM_DATA_%s'%ii, wfdat,'%sH'%lenwfdat))
            ii+=1
        kk=1
        #nrep = self._awg_nrep

        seq_record_str = StringIO()
        for segment in wfname_l.transpose():
            seq_record_str.write(
                    self._pack_record('SEQUENCE_WAIT_%s'%kk, trig_wait[kk-1],'h')+\
                            self._pack_record('SEQUENCE_LOOP_%s'%kk, int(nrep[kk-1]),'l')+\
                            self._pack_record('SEQUENCE_JUMP_%s'%kk, jump_to[kk-1],'h')+\
                            self._pack_record('SEQUENCE_GOTO_%s'%kk, goto_state[kk-1],'h')
                            )
            for wfname in segment:

                if wfname is not None:

                    ch = wfname[-1]
                    #print wfname,'SEQUENCE_WAVEFORM_NAME_CH_'+ch+'_%s'%kk
                    seq_record_str.write(
                            self._pack_record('SEQUENCE_WAVEFORM_NAME_CH_'+ch+'_%s'%kk, wfname+'\x00','%ss'%len(wfname+'\x00'))
                            )
            kk+=1

        self.awg_file = head+record_str.getvalue()+seq_record_str.getvalue()


    def get_attribute(self, att_name):
        exec('retval = self.%s'%att_name)
        return retval
    def get_awg_file(self):
        return self.awg_file

    def _pack_record(self,name,value,dtype):
        '''
        packs awg_file record structure: '<I(lenname)I(lendat)s[data of dtype]'
        '''
        #print name,dtype

        if len(dtype)==1:
            #print 'dtype:1'
            dat = struct.pack('<'+dtype,value)
            lendat=len(dat)
            #print 'name: ',name, 'dtype: ',dtype, 'len: ',lendat, 'vali: ',value
        else:
            #print 'dtype:>1'
            if dtype[-1] == 's':
                dat = struct.pack(dtype,value)
                lendat = len(dat)
                #print 'name: ',name, 'dtype: ',dtype, 'len: ',lendat, 'vals: ',len(value)
            else:
                #print tuple(value)
                dat = struct.pack('<'+dtype,*tuple(value))
                lendat = len(dat)
                #print 'name: ',name, 'dtype: ',dtype, 'len: ',lendat, 'vals: ',len(value)
        #print lendat
        return struct.pack('<II',len(name+'\x00'),lendat) + name + '\x00' + dat



    def set_sequence(self,packed_waveforms,wfname_l,delay_labs, nrep_l, wait_l, goto_l, logic_jump_l, clock=1e9):
        '''
        sets the AWG in sequence mode and loads waveforms into the sequence.
        packed_waveforms: dictionary containing packed waveforms with keys wfname_l and delay_labs
        wfname_l = np.array of waveform names [[wf1_ch1,wf2_ch1..],[wf1_ch2,wf2_ch2..],...]
        delay_labs = list of length len(channels) for a waveform that is repeated in between segments
        nrep_l = list specifying the number of reps for each seq element
        wait_l = idem for wait_trigger_state
        goto_l = idem for goto_state (goto is the element where it hops to in case the element is finished)
        logic_jump_l = idem for event_jump_to (event or logic jump is the element where it hops in case of an event)

        '''
        n_ch = len(wfname_l)
        chi=0
        group=[]
        len_sq = len(nrep_l)


        AWG = qt.instruments['AWG']#self._AWG_list[k]
        ch = 4#self._AWG_properties[k]['channels']
        if AWG.get_type() =='Tektronix_AWG5014_09':
            self.generate_awg_file(packed_waveforms,wfname_l[chi:(chi+ch)],delay_labs[chi:(chi+ch)], nrep_l, wait_l, goto_l, logic_jump_l, clock)
            AWG.set_awg_file(self.awg_file)
        else:
            print AWG.get_type(), ' not supported, sequence not loaded!!!'

        chi=ch

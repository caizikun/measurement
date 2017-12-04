import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import DD_2 as DD
import pulse_select as ps
import sys



class ElectronRabi(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        # X = pulselib.HermitePulse_Envelope_IQ('MW pulse',
        #     I_channel = 'MW_Imod',
        #     Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True)
        print 'MBI at', self.params['AWG_MBI_MW_pulse_ssbmod_frq']
        print 'MW rotations at', self.params['MW_pulse_mod_frqs'][i]
        # program AWG
        if upload:
            #qt.pulsar.upload(mbi_elt, *elts)
            qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        #qt.pulsar.program_sequence(seq)






class NitrogenRabiDirectRF(pulsar_msmt.MBI):
    """
    MJD 201711
    Measurement class for a Rabi flop with direct RF
    Input:
        name(string): Name of the measurement you want to run
    
    Uploads a measurement sequence to the AWG

    Nitrogen init: weak e Pi pulse 
    Nitrogen manip: RF sequence
    Nitrogen RO:   weak e Pi pulse


    """

    mprefix = 'PulsarMBINitrogenRabi'

    def _RO_element(self,name ='RO weak pi'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)


        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel='MW_switch',
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        ro_element = element.Element(name, pulsar=qt.pulsar)
        ro_element.append(T)
        ro_element.append(X)
        ro_element.append(adwin_sync)

        return ro_element


    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        ro_elt = self._RO_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # # define the necessary pulses
        # T = pulse.SquarePulse(channel='MW_pulsemod',
        #     length = 100e-9, amplitude = 0)


        # X = pulselib.MW_IQmod_pulse('MBI MW pulse',
        #     I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
        #     amplitude = self.params['AWG_MBI_MW_pulse_amp'],
        #     length = self.params['AWG_MBI_MW_pulse_duration'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'])

        # # the actual element
        # ro_element = element.Element(name, pulsar=qt.pulsar)
        # ro_element.append(T)
        # ro_element.append(X)

        N_pulse = pulselib.RF_erf_envelope(channel = 'RF', amplitude = self.params['RF_pulse_amp'],
            frequency = self.params['RF_pulse_frqs'])

        # X = pulselib.HermitePulse_Envelope_IQ('MW pulse',
        #     I_channel = 'MW_Imod',
        #     Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []

        for i in range(self.params['pts']):
            e = element.Element('RF_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(pulse.cp(T, length = 500e-9))
            e.append(
                    pulse.cp(N_pulse, length=self.params['RF_pulse_length'][i], frequency = self.params['RF_pulse_frqs']))
            e.append(pulse.cp(T, length = 500e-9))


            # for j in range(self.params['MW_pulse_multiplicities'][i]):
            #     e.append(
            #         pulse.cp(X,
            #             frequency = self.params['MW_pulse_mod_frqs'][i],
            #             amplitude = self.params['MW_pulse_amps'][i],
            #             length = self.params['MW_pulse_durations'][i]))
            #     e.append(
            #         pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            #e.append(adwin_sync)
            elts.append(e)

        # gate_seq = []
        # for pt in range(self.params['pts']):
        #     rabi_pulse = DD.Gate('Rabi_pulse_'+str(pt),'RF_pulse',
        #         length      = self.params['RF_pulse_durations'][pt],
        #         RFfreq      = self.params['RF_pulse_frqs'][pt],
        #         amplitude   = self.params['RF_pulse_amps'][pt])
        #     gate_seq.extend([rabi_pulse])
        #     print 'Gate_seq', gate_seq

        #     gate_seq = DD.NitrogenRabiWithDirectRF.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

        # ### Convert elements to AWG sequence and add to combined list
        # list_of_elements, seq2 = DD.combine_to_AWG_sequence(gate_seq, explicit=True)




        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True) #True
            seq.append(name = 'RO_pt-%d' % i, wfname = ro_elt.name,
                trigger_wait = False)

            # seq.append(name = 'RO-%d' % i, wfname = mbi_elt.name,
            #     trigger_wait = False)      ## According to Norbert the trigger wait time should be set to False. 
            ## This is implemented at the beginning of the MBI because it is waiting for a CR check from the adwin. 
            ## For the readout this doesn't have to be implemented because it is deterministic. 
        print 'MBI at', self.params['AWG_MBI_MW_pulse_ssbmod_frq']
        # print 'MW rotations at', self.params['MW_pulse_mod_frqs'][i]
        # program AWG
        if upload:
            #qt.pulsar.upload(mbi_elt, *elts)
            qt.pulsar.program_awg(seq, mbi_elt, ro_elt, *elts , debug=debug)
        #qt.pulsar.program_sequence(seq)




class ElectronRamsey(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRamsey'

    def generate_sequence(self, upload=True, debug = False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.append(
                pulse.cp(X,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_amps'][i],
                    length = self.params['MW_pulse_durations'][i],
                    phase = self.params['MW_pulse_1_phases'][i]))

            e.append(
                pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            e.append(
                pulse.cp(X,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_2_amps'][i],
                    length = self.params['MW_pulse_2_durations'][i],
                    phase = self.params['MW_pulse_2_phases'][i]))

            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True)

        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        

class ElectronRamsey_Dephasing(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRamsey_Dephasing'

    # def setup(self):
    #     MBI.setup() # enable the second MW source.

    def generate_sequence(self, upload=True, debug = False):


        #configure the dephasing beam. power and AWG channel
        
        dephasing_AOM_voltage=qt.instruments[self.params['dephasing_AOM']].power_to_voltage(self.params['laser_dephasing_amplitude'],controller='sec')
        if dephasing_AOM_voltage > (qt.instruments[self.params['dephasing_AOM']]).get_sec_V_max():
            print 'Suggested power level would exceed V_max of the AOM driver.'
        else:
            #not sure if the secondary channel of an AOM can be obtained in this way?
            channelDict={'ch2m1': 'ch2_marker1','ch2m2':'ch2_marker2','ch4m1':'ch4_marker1'}
            print 'AOM voltage', dephasing_AOM_voltage
            self.params['Channel_alias']=qt.pulsar.get_channel_name_by_id(channelDict[qt.instruments[self.params['dephasing_AOM']].get_sec_channel()])
            qt.pulsar.set_channel_opt(self.params['Channel_alias'],'high',dephasing_AOM_voltage)
            print self.params['Channel_alias']

        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(name='syncpulse', channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        Dephasing = pulse.SquarePulse(channel=self.params['Channel_alias'],
            length = 1000e-9, amplitude = dephasing_AOM_voltage)

        X = ps.X_pulse(self)
        try:
            Pi_mw2 = ps.pi_pulse_MW2(self)
        except:
            print 'No parameters for second MW source found'
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            try :
                init_with_second_source = self.params['init_with_second_source']
                init_in_zero = self.params['init_in_zero']
            except: 
                print 'Cannot init. Parameter not defined?'
                init_with_second_source = False
                init_in_zero = False

            if init_with_second_source:
                e.append(pulse.cp(Pi_mw2, 
                    length = self.params['MW_pulse_durations'][i],
                    amplitude = self.params['MW_pulse_amps'][i]))
            elif not init_in_zero:
                e.append(
                pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i],
                        phase = self.params['MW_pulse_1_phases'][i]))

            e.append(pulse.cp(T, length=self.params['MW_repump_delay1'][i]))

            try: #MW2 used for repumping
                pump_using_newfocus = self.params['pump_using_newfocus']
                pump_using_repumper = self.params['pump_using_repumper']
            except:
                print 'pump using NF not defined, set default: True'
                pump_using_newfocus = True
                pump_using_repumper = False
            if self.params['repumping_time'][i] != 0 and pump_using_newfocus:
                e.append(pulse.cp(Dephasing, length=self.params['repumping_time'][i]))
            if self.params['repumping_time'][i] != 0 and pump_using_repumper:
                if pump_using_newfocus:
                    e.append(pulse.cp(T, length=-self.params['repumping_time'][i]))
                e.append(pulse.cp(
                    Dephasing, channel='AOM_Repumper', length=self.params['repumping_time'][i], 
                    amplitude= qt.instruments['RepumperAOM'].power_to_voltage(self.params['repumper_amplitude']) ))
            
            try: #MW2 used for repumping
                pump_using_MW2 = self.params['pump_using_MW2']
                if pump_using_MW2 and (self.params['pump_MW2_durations'][i]-2*self.params['pump_MW2_falltime'][i]) > 0:
                    #print self.params['pump_MW2_delay'][i]
                    e.append(pulse.cp(T, length=-self.params['repumping_time'][i]+self.params['pump_MW2_delay'][i] ))
                    e.append(
                         pulse.cp(Pi_mw2,
                             length = (self.params['pump_MW2_durations'][i]-2*self.params['pump_MW2_falltime'][i]),
                             amplitude = self.params['MW2_pulse_amplitudes'][i]))
            except:
                print 'Exception in pump using MW2: ', sys.exc_info()

            e.append(
                pulse.cp(T, length=self.params['MW_repump_delay2'][i]))


            do_BB1 = False   #Readout in pm1 basis
            if do_BB1 and self.params['MW_pulse_2_amps'][i] != 0:
                # necessary defs for BB1
                T_BB1 =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                        length = 5*self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2, 
                        amplitude = 0.)
                # T_rep_BB1 = pulse.SquarePulse(channel='adwin_sync',name='Wait t-trep',
                #         length = t-t_rep-5*self.params['fast_pi_duration']/2, amplitude = 0.)
                X_BB1 = pulse.cp(X,length = self.params['BB1_fast_pi_duration'],
                    amplitude = self.params['BB1_fast_pi_amp'])
                BB1_phase1 = pulse.cp(X_BB1, phase = self.params['X_phase']+104.5)
                BB1_phase2 = pulse.cp(X_BB1, phase = self.params['X_phase']+313.4)
                e.append(T_BB1)
                e.append(BB1_phase1)
                e.append(BB1_phase2)
                e.append(BB1_phase2)
                e.append(BB1_phase1)
                e.append(X_BB1)
            elif self.params['MW_pulse_2_amps'][i] != 0 and self.params['readout_with_second_source']:
                e.append(pulse.cp(Pi_mw2, 
                    length = self.params['MW_pulse_2_durations'][i],
                    amplitude = self.params['MW_pulse_2_amps'][i]))
            elif self.params['MW_pulse_2_amps'][i] != 0 and self.params['readout_with_second_source'] == False:
                e.append(pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_2_amps'][i],
                        length = self.params['MW_pulse_2_durations'][i],
                        phase = self.params['MW_pulse_2_phases'][i]))
            
            e.append(pulse.cp(T, length=2e-6))
            # e.append(adwin_sync)
            elts.append(e)

        # sequence
        # seq = pulsar.Sequence('MBI Electron Ramsey sequence')
        # for i,e in enumerate(elts):
        #     seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
        #         trigger_wait = True, goto_target = 'MBI-%d' % i,
        #         jump_target = e.name)
        #     seq.append(name = e.name, wfname = e.name,
        #         trigger_wait = True)

        # program AWG
            # e = element.Element('Adwin_sync_pt-%d' % i, pulsar=qt.pulsar,
            #     global_time = True)
            # e.append(adwin_sync)
            # elts.append(e)

        adwin_elt = element.Element('Adwin_sync', pulsar=qt.pulsar,
                        global_time = True)
        adwin_elt.append(adwin_sync)
        # sequence
        print len(elts)
        seq = pulsar.Sequence('MBI Electron Ramsey sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True,repetitions = self.params['Repump_multiplicity'][i])
            seq.append(name = 'Adwin-sync-%d' % i, wfname = adwin_elt.name,
                trigger_wait = False)


        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, mbi_elt,adwin_elt, *elts , debug=debug)
        # if upload:
        #     qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        
class Simple_Electron_repumping(pulsar_msmt.MBI):
    """
    Simple measurement for repumping of the electron spin.
    All you need is a repump laser on an AWG marker channel and
    the ability to do MW pi pulses. 
    """
    mprefix = 'PulsarMBIElectronRamsey_Dephasing'

    # def setup(self):
    #     MBI.setup() # enable the second MW source.

    def generate_sequence(self, upload=True, debug = False):

        #configure the repumping beam. power and AWG channel
        
        repumping_AOM_voltage=qt.instruments[self.params['repump_AOM']].power_to_voltage(self.params['laser_repump_amplitude'],controller='sec')
        if repumping_AOM_voltage > (qt.instruments[self.params['repump_AOM']]).get_sec_V_max():
            print 'Suggested power level would exceed V_max of the AOM driver.'
            return
        else:
            #not sure if the secondary channel of an AOM can be obtained in this way?
            channelDict={'ch2m1': 'ch2_marker1','ch2m2':'ch2_marker2', 'ch4m1':'ch4_marker1'}
            print 'AOM voltage', repumping_AOM_voltage
            print self.params['repump_AOM'] 
            self.params['Channel_alias']=qt.pulsar.get_channel_name_by_id(channelDict[qt.instruments[self.params['repump_AOM']].get_sec_channel()])
            qt.pulsar.set_channel_opt(self.params['Channel_alias'],'high',repumping_AOM_voltage)
            print self.params['Channel_alias']

        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(name='syncpulse', channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        #Called dephasing, but does repump...
        Dephasing = pulse.SquarePulse(channel=self.params['Channel_alias'],
            length = 1000e-9, amplitude = repumping_AOM_voltage) 

        X = ps.X_pulse(self)
        X_mw2 = ps.pi_pulse_MW2(self)
        if False: #optical pumping using p1 transition
            squareX = ps.mw2_squareX(self)
        else: #optical pumping using m1 transition
            squareX = ps.squareX(self)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)

            e.append(T)
            
            #initialize the electron after pumping to 0
            if self.params['init_state'] == 'm1':
                e.append(pulse.cp(X)) 
            elif self.params['init_state'] == 'p1':
                e.append(pulse.cp(X_mw2))
            else: # init in zero
                pass

            e.append(pulse.cp(T, length=self.params['MW_repump_delay1'][i]))

            pump_cycle_no = 0
            while pump_cycle_no < self.params['pumping_cycles']:
                pump_cycle_no += 1
                if self.params['repumping_time'][i] != 0:
                    if pump_cycle_no>1:
                        e.append(pulse.cp(T, length=self.params['delay_before_MW'][i]))
                        e.append(pulse.cp(squareX))
                        e.append(pulse.cp(T, length=self.params['delay_after_MW'][i]))
                    e.append(pulse.cp(Dephasing, length=self.params['repumping_time'][i]))


            e.append(
                pulse.cp(T, length=self.params['MW_repump_delay2'][i]))

            #initialize the electron after pumping to 0
            if self.params['ro_state'] == 'm1':
                e.append(pulse.cp(X)) 
            elif self.params['ro_state'] == 'p1':
                e.append(pulse.cp(X_mw2))
            else: # ro zero
                pass

            e.append(pulse.cp(T, length=2e-6))

            elts.append(e)

        adwin_elt = element.Element('Adwin_sync', pulsar=qt.pulsar,
                        global_time = True)
        adwin_elt.append(adwin_sync)

        seq = pulsar.Sequence('MBI Electron Ramsey sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True, repetitions = self.params['Repump_multiplicity'][i])
            seq.append(name = 'Adwin-sync-%d' % i, wfname = adwin_elt.name,
                trigger_wait = False)


        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, mbi_elt,adwin_elt, *elts , debug=debug)

class ElectronRabiSplitMultElements(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        pulse_elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar)
            e.append(T)
            e.append(
                pulse.cp(X,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_amps'][i],
                    length = self.params['MW_pulse_durations'][i]))

            # e.append(adwin_sync)
            pulse_elts.append(e)

        wait_elt = element.Element('pulse_delay', pulsar=qt.pulsar)
        wait_elt.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        sync_elt.append(adwin_sync)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(pulse_elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name+'-0')

            if self.params['MW_pulse_multiplicities'][i] == 0:
                seq.append(name = e.name+'-0', wfname = wait_elt.name,
                    trigger_wait = True)
            else:
                for j in range(self.params['MW_pulse_multiplicities'][i]):
                    seq.append(name = e.name+'-%d' % j, wfname = e.name,
                        trigger_wait = (j==0) )
                    seq.append(name = 'wait-%d-%d' % (i,j), wfname=wait_elt.name,
                        repetitions = int(self.params['MW_pulse_delays'][i]/1e-6))

            seq.append(name = 'sync-%d' % i, wfname=sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, mbi_elt, wait_elt, sync_elt, *pulse_elts, debug=debug)

class ElectronRabi_Switch(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def _MBI_element(self,name ='MBI CNOT'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        mbi_element = element.Element(name, pulsar=qt.pulsar)
        mbi_element.append(T)
        mbi_element.append(X)
        mbi_element.append(adwin_sync)

        return mbi_element

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel='MW_switch',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'] )

        # X = pulselib.HermitePulse_Envelope_IQ('MW pulse',
        #     I_channel = 'MW_Imod',
        #     Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True)
        print 'MBI at', self.params['AWG_MBI_MW_pulse_ssbmod_frq']
        print 'MW rotations at', self.params['MW_pulse_mod_frqs'][i]
        # program AWG
        if upload:
            #qt.pulsar.upload(mbi_elt, *elts)
            qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        #qt.pulsar.program_sequence(seq)

class ElectronRabiSplitMultElements_Switch(pulsar_msmt.MBI):
    mprefix = 'PulsarMBIElectronRabi'

    def _MBI_element(self,name ='MBI CNOT'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel='MW_switch',
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        mbi_element = element.Element(name, pulsar=qt.pulsar)
        mbi_element.append(T)
        mbi_element.append(X)
        mbi_element.append(adwin_sync)

        return mbi_element

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel='MW_switch',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        pulse_elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar)
            e.append(T)
            e.append(
                pulse.cp(X,
                    frequency = self.params['MW_pulse_mod_frqs'][i],
                    amplitude = self.params['MW_pulse_amps'][i],
                    length = self.params['MW_pulse_durations'][i]))

            # e.append(adwin_sync)
            pulse_elts.append(e)

        wait_elt = element.Element('pulse_delay', pulsar=qt.pulsar)
        wait_elt.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        sync_elt.append(adwin_sync)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(pulse_elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name+'-0')

            if self.params['MW_pulse_multiplicities'][i] == 0:
                seq.append(name = e.name+'-0', wfname = wait_elt.name,
                    trigger_wait = True)
            else:
                for j in range(self.params['MW_pulse_multiplicities'][i]):
                    seq.append(name = e.name+'-%d' % j, wfname = e.name,
                        trigger_wait = (j==0) )
                    seq.append(name = 'wait-%d-%d' % (i,j), wfname=wait_elt.name,
                        repetitions = int(self.params['MW_pulse_delays'][i]/1e-6))

            seq.append(name = 'sync-%d' % i, wfname=sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, mbi_elt, wait_elt, sync_elt, *pulse_elts, debug=debug)
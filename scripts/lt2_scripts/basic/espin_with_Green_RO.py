"""
Script doing spin manipulation and readout with green using the qutau.
"""

import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_qutau
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

reload(pulsar_qutau)

SAMPLE_CFG = qt.exp_params['protocols']['current']
print SAMPLE_CFG
SAMPLE_NAME =  qt.exp_params['samples']['current']

qutau=qt.instruments['QuTau']

class Green_RO(pulsar_qutau.QuTauPulsarMeasurementIntegrated):

    def autoconfig(self, **kw):
        self.params['send_AWG_start'] = 1
        self.params['wait_for_AWG_done'] = 1


        self.params['Green_RO_Voltage_AWG'] = \
                self.AWG_RO_AOM.power_to_voltage(self.params['Green_RO_power'], controller='sec')
        qt.pulsar.set_channel_opt('AOM_Green', 'high', self.params['Green_RO_Voltage_AWG'])

        pulsar_qutau.QuTauPulsarMeasurementIntegrated.autoconfig(self, **kw)

    # Most basic MW sequence consisting of 1 pulse (used for DESR or Rabi for instance)
    def generate_sequence(self, upload=True):

        #define the pulses
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)
        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 2500e-9, #was 1590e-9 NK
          amplitude = 2)
        X = pulselib.MW_IQmod_pulse('Rabi_MW_pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=500e-9)

        seq=pulsar.Sequence('RabiOsci sequence')
        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait2',refpulse='init')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        print self.params['MW_modulation_frequencies']
        seq.append(name=init.name,wfname=init.name,trigger_wait=True)
        for k,t in enumerate(self.params['sweep_pts']):

            e=element.Element('Rabi_length-%d' % k,pulsar=qt.pulsar)
            if k==0:
                first_dp_element=e.name
            e.add(T(length=2000e-9),name='wait')
            e.add(adwin_trigger_pulse,name='adwin_trigger',refpulse='wait',refpoint='start')

            e.add(X(length=self.params['MW_pulse_durations'][k],frequency= self.params['MW_modulation_frequencies'][k]),name='MWpulse',refpulse='wait',refpoint='end')
            e.add(T,name='wait2',refpulse='MWpulse',refpoint='end')
            e.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
            e.add(sync,name='Sync',refpulse='wait2',refpoint='end')
            e.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
            e.add(sync,name='Sync2',refpulse='wait3',refpoint='end')
            
            elements.append(e)
            seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)

        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)
        seq.append(name=end.name,wfname=end.name,goto_target=first_dp_element,jump_target=init.name)
            

        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq,loop=False)
            else:
                qt.pulsar.program_awg(seq,*elements,loop=False)

    def measure(self,debug=False,upload=True):
        self.autoconfig()
        self.generate_sequence(upload=upload)

        self.setup(mw=True, debug=debug)
        self.params['MAX_SYNC_BIN'] = int((self.params['GreenAOM_pulse_length'] +1e-6)/(2**(self.params['BINSIZE']-1)*qutau.get_timebase())) # TODO Write more general!
        self.params['DT_SYNC_BIN'] = int((self.params['pq_sync_length']+self.params['time_between_syncs']+5e-9)/(2**(self.params['BINSIZE']-1)*qutau.get_timebase())) # TODO Write more general!

        self.run(autoconfig=False, setup=False, debug=debug)    
        self.save()
        self.finish(save_ins_settings=False)
        self.params['missed_syncs']=self.params['syncs_per_sweep']*self.params['pts']*self.params['repetitions'] - self.nr_of_syncs
        return self.params['missed_syncs'],self.params['syncs_per_sweep']*self.params['pts']*self.params['repetitions']

class GreenRO_T1(Green_RO):


    def generate_sequence(self, upload=True):

        #define the pulses
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 1590e-9,   amplitude = 2)
        # X = pulselib.MW_IQmod_pulse('Rabi_MW_pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod',
        #     amplitude = self.params['fast_pi2_amp'],
        #     frequency = self.params['fast_pi2_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'])
        # X_pi = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod',
        #     amplitude = self.params['fast_pi_amp'],
        #     frequency = self.params['fast_pi_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     length = self.params['fast_pi_duration'],
        #     phase =  self.params['X_phase'])
        wait_before_RO = 50e-9
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=wait_before_RO)

        seq=pulsar.Sequence('T1 sequence')
        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        
        seq.append(name=init.name,wfname=init.name,trigger_wait=True)
        for k,t in enumerate(self.params['wait_times']):

            e=element.Element('T1-%d' % k,pulsar=qt.pulsar,global_time=True)
            if k==0:
                first_dp_element=e.name
            e.add(T(length=1500e-9),name='wait')
            e.add(adwin_trigger_pulse,name='adwin_trigger',refpulse='wait',refpoint='start')
            elements.append(e)
            seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
            # e.add(X(length=self.params['fast_pi2_duration'],phase=0),name='MWpulse',refpulse='wait',refpoint='end')
            
            nr_T_elt_reps = self.params['wait_times'][k]/self.params['wait_time_repeat_element']

            # if waiting times are long: implement tau by repeating a 'wait_time_repeat_element' in AWG. Saves memory
            if nr_T_elt_reps > 0: 
                # Implement one waiting period tau
                # free_evol_us=int(self.params['free_evolution_times'][k]*1e6)-4

                # free_evol_around_pi2=(self.params['free_evolution_times'][k]-free_evol_us*1e-6)/2.
                # e.add(T(length=free_evol_around_pi2),name='tau_1_first_part',refpulse='MWpulse',refpoint='end')
                # elements.append(e)
                # t_offset=e.length()    
                # seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
                
                e=element.Element('T1-waiting_time-%d' % k,pulsar=qt.pulsar,global_time=True)
                # e.add(T(length=1e-6),name='tau')
                e.add(T(length = self.params['wait_time_repeat_element'] * 1e-6))
                elements.append(e)
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name,repetitions=nr_T_elt_reps)
                refpulse_for_RO = e.name 
                # t_offset+=e.length()*free_evol_us                # make sure two pi/2 pulses (27-3-2015: pi/2 pulse and pi pulse?) have same time reference
                # e=element.Element('Hahn-%d-tau_1_second_part' % k,pulsar=qt.pulsar,global_time=True,time_offset=t_offset)
                # e.add(T(length=free_evol_around_pi2),name='tau_1_third_part')

                # # X Pi pulse
                # e.add(X_pi(), name = 'pi_pulse', refpulse = 'tau_1_third_part', refpoint = 'end')

                # Implement one waiting period tau
                # free_evol_us=int(self.params['free_evolution_times'][k]*1e6)-4

                # free_evol_around_pi2=(self.params['free_evolution_times'][k]-free_evol_us*1e-6)/2.
                # e.add(T(length=free_evol_around_pi2),name='tau_2_first_part',refpulse='pi_pulse',refpoint='end')
                # elements.append(e)
                # t_offset=e.length()    
                # seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
                
                # e=element.Element('Hahn-%d-tau_2_waiting_time' % k,pulsar=qt.pulsar,global_time=True)
                # e.add(T(length=1e-6),name='tau')
                # elements.append(e)
                # seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name,repetitions=free_evol_us)

                # t_offset+=e.length()*free_evol_us                # make sure two pi/2 pulses (27-3-2015: pi/2 pulse and pi pulse?) have same time reference
                # e=element.Element('Hahn-%d-tau_2_second_part' % k,pulsar=qt.pulsar,global_time=True,time_offset=t_offset)
                # e.add(T(length=free_evol_around_pi2),name='tau_2_third_part')

                # Last pi/2 pulse
                # e.add(X(length=self.params['fast_pi2_duration'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau_2_third_part',refpoint='end')
                # e.add(X(length=self.params['fast_pi2_duration'],phase=180),name='MWpulse2',refpulse='tau_2_third_part',refpoint='end')
            elif self.params['wait_times'][k] > 0: # Don't create element of zero duration
                e=element.Element('T1-waiting_time-%d' % k,pulsar=qt.pulsar,global_time=True)
                # e.add(T(length=self.params['wait_times'][k]), name = 'tau1', refpulse = 'MWpulse', refpoint ='end')
                e.add(T(length=self.params['wait_times'][k]))
                elements.append(e)
                seq.append(name = e.name, wfname = e.name, trigger_wait = False, jump_target = init.name)
                refpulse_for_RO = e.name 
                # e.add(X_pi(), name = 'pi_pulse', refpulse = 'tau1', refpoint = 'end')
                # e.add(T(length=self.params['wait_times'][k]),name='tau2',refpulse='tau1',refpoint='end')
                # e.add(X(length=self.params['fast_pi2_duration'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau2',refpoint='end')
                # pi/2 (-x)
                # e.add(X(length=self.params['fast_pi2_duration'],phase=180),name='MWpulse2',refpulse='tau2',refpoint='end')
            e=element.Element('Readout-%d' % k,pulsar=qt.pulsar,global_time=True)
            # e.add(T,name='wait2',refpulse=refpulse_for_RO,refpoint='end')
            e.add(T,name='wait2')
            e.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
            e.add(sync,name='Sync',refpulse='wait2',refpoint='end')
            e.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
            e.add(sync,name='Sync2',refpulse='wait3',refpoint='end')
            
            elements.append(e)
            seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)

        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)
        seq.append(name=end.name,wfname=end.name,goto_target=first_dp_element,jump_target=init.name)

        #create a sequence from the gathered elements
        
        #for e in elements:
            

        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq,loop=False)
            else:
                qt.pulsar.program_awg(seq,*elements,loop=False)

class GreenRO_Ramsey(Green_RO):

    def generate_sequence(self, upload=True):

        #define the pulses
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 1590e-9,   amplitude = 2)
        X = pulselib.MW_IQmod_pulse('Rabi_MW_pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['Square_pi2_amp'],
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        wait_before_MW = 500e-9
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=wait_before_MW)

        seq=pulsar.Sequence('Ramsey sequence')
        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        
        seq.append(name=init.name,wfname=init.name,trigger_wait=True)
        for k,t in enumerate(self.params['sweep_pts']):

            e=element.Element('Ramsey-%d' % k,pulsar=qt.pulsar,global_time=True)
            if k==0:
                first_dp_element=e.name
            e.add(T(length=1500e-9),name='wait')
            e.add(adwin_trigger_pulse,name='adwin_trigger',refpulse='wait',refpoint='start')
            e.add(X(length=self.params['Square_pi2_length'],phase=0),name='MWpulse',refpulse='wait',refpoint='end')
            
            # if waiting times are long: implement tau by repeating a 1 us element in AWG. Saves memory
            if self.params['free_evolution_times'][k] >5e-6: 
                free_evol_us=int(self.params['free_evolution_times'][k]*1e6)-4

                free_evol_around_pi2=(self.params['free_evolution_times'][k]-free_evol_us*1e-6)/2.
                e.add(T(length=free_evol_around_pi2),name='tau_first_part',refpulse='MWpulse',refpoint='end')
                elements.append(e)
                t_offset=e.length()    
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
                
                e=element.Element('Ramsey-%d-waiting_time' % k,pulsar=qt.pulsar,global_time=True)
                e.add(T(length=1e-6),name='tau')
                elements.append(e)
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name,repetitions=free_evol_us)

                t_offset+=e.length()*free_evol_us                # make sure two pi/2 pulses have same time reference
                e=element.Element('Ramsey-%d-second_part' % k,pulsar=qt.pulsar,global_time=True,time_offset=t_offset)
                e.add(T(length=free_evol_around_pi2),name='tau_third_part')
                e.add(X(length=self.params['Square_pi2_length'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau_third_part',refpoint='end')
            else:
                e.add(T(length=self.params['free_evolution_times'][k]),name='tau',refpulse='MWpulse',refpoint='end')
                e.add(X(length=self.params['Square_pi2_length'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau',refpoint='end')
            e.add(T,name='wait2',refpulse='MWpulse2',refpoint='end')
            e.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
            e.add(sync,name='Sync',refpulse='wait2',refpoint='end')
            e.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
            e.add(sync,name='Sync2',refpulse='wait3',refpoint='end')
            
            elements.append(e)
            seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)

        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)
        seq.append(name=end.name,wfname=end.name,goto_target=first_dp_element,jump_target=init.name)

        #create a sequence from the gathered elements
        
        #for e in elements:
            

        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq,loop=False)
            else:
                qt.pulsar.program_awg(seq,*elements,loop=False)

class GreenRO_Hahn(Green_RO):

    # def create_element_long_tau(self):
    #     '''
    #     Creates a waiting element tau > 5 us by repeating 1 us long elements. This saves memory in AWG.
    #     Structure of resulting tau element = (2 us wait) + (tau - 4) x (1 us wait) + (2 us wait)
    #     '''

    def generate_sequence(self, upload=True):

        #define the pulses
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 1590e-9,   amplitude = 2)
        X = pulselib.MW_IQmod_pulse('Rabi_MW_pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['fast_pi2_amp'],
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        X_pi = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['fast_pi_amp'],
            frequency = self.params['fast_pi_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            phase =  self.params['X_phase'])
        wait_before_MW = 500e-9
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=wait_before_MW)

        seq=pulsar.Sequence('Hahn sequence')
        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        
        seq.append(name=init.name,wfname=init.name,trigger_wait=True)
        for k,t in enumerate(self.params['sweep_pts']):

            e=element.Element('Hahn-%d' % k,pulsar=qt.pulsar,global_time=True)
            if k==0:
                first_dp_element=e.name
            e.add(T(length=1500e-9),name='wait')
            e.add(adwin_trigger_pulse,name='adwin_trigger',refpulse='wait',refpoint='start')
            e.add(X(length=self.params['fast_pi2_duration'],phase=0),name='MWpulse',refpulse='wait',refpoint='end')
            
            # if waiting times are long: implement tau by repeating a 1 us element in AWG. Saves memory
            if self.params['free_evolution_times'][k] > 5e-6: 
                # Implement one waiting period tau
                free_evol_us=int(self.params['free_evolution_times'][k]*1e6)-4

                free_evol_around_pi2=(self.params['free_evolution_times'][k]-free_evol_us*1e-6)/2.
                e.add(T(length=free_evol_around_pi2),name='tau_1_first_part',refpulse='MWpulse',refpoint='end')
                elements.append(e)
                t_offset=e.length()    
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
                
                e=element.Element('Hahn-%d-tau_1_waiting_time' % k,pulsar=qt.pulsar,global_time=True)
                e.add(T(length=1e-6),name='tau')
                elements.append(e)
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name,repetitions=free_evol_us)

                t_offset+=e.length()*free_evol_us                # make sure two pi/2 pulses (27-3-2015: pi/2 pulse and pi pulse?) have same time reference
                e=element.Element('Hahn-%d-tau_1_second_part' % k,pulsar=qt.pulsar,global_time=True,time_offset=t_offset)
                e.add(T(length=free_evol_around_pi2),name='tau_1_third_part')

                # # X Pi pulse
                e.add(X_pi(), name = 'pi_pulse', refpulse = 'tau_1_third_part', refpoint = 'end')

                # Implement one waiting period tau
                free_evol_us=int(self.params['free_evolution_times'][k]*1e6)-4

                free_evol_around_pi2=(self.params['free_evolution_times'][k]-free_evol_us*1e-6)/2.
                e.add(T(length=free_evol_around_pi2),name='tau_2_first_part',refpulse='pi_pulse',refpoint='end')
                elements.append(e)
                t_offset=e.length()    
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)
                
                e=element.Element('Hahn-%d-tau_2_waiting_time' % k,pulsar=qt.pulsar,global_time=True)
                e.add(T(length=1e-6),name='tau')
                elements.append(e)
                seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name,repetitions=free_evol_us)

                t_offset+=e.length()*free_evol_us                # make sure two pi/2 pulses (27-3-2015: pi/2 pulse and pi pulse?) have same time reference
                e=element.Element('Hahn-%d-tau_2_second_part' % k,pulsar=qt.pulsar,global_time=True,time_offset=t_offset)
                e.add(T(length=free_evol_around_pi2),name='tau_2_third_part')

                # Last pi/2 pulse
                # e.add(X(length=self.params['fast_pi2_duration'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau_2_third_part',refpoint='end')
                e.add(X(length=self.params['fast_pi2_duration'],phase=180),name='MWpulse2',refpulse='tau_2_third_part',refpoint='end')
            else:
                e.add(T(length=self.params['free_evolution_times'][k]), name = 'tau1', refpulse = 'MWpulse', refpoint ='end')
                e.add(X_pi(), name = 'pi_pulse', refpulse = 'tau1', refpoint = 'end')
                e.add(T(length=self.params['free_evolution_times'][k]),name='tau2',refpulse='tau1',refpoint='end')
                # e.add(X(length=self.params['fast_pi2_duration'],phase=self.params['second_pi2_phases'][k]),name='MWpulse2',refpulse='tau2',refpoint='end')
                # pi/2 (-x)
                e.add(X(length=self.params['fast_pi2_duration'],phase=180),name='MWpulse2',refpulse='tau2',refpoint='end')
            e.add(T,name='wait2',refpulse='MWpulse2',refpoint='end')
            e.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
            e.add(sync,name='Sync',refpulse='wait2',refpoint='end')
            e.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
            e.add(sync,name='Sync2',refpulse='wait3',refpoint='end')
            
            elements.append(e)
            seq.append(name=e.name,wfname=e.name,trigger_wait=False,jump_target=init.name)

        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)
        seq.append(name=end.name,wfname=end.name,goto_target=first_dp_element,jump_target=init.name)

        #create a sequence from the gathered elements
        
        #for e in elements:
            

        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq,loop=False)
            else:
                qt.pulsar.program_awg(seq,*elements,loop=False)

def T1(name):
    m = GreenRO_T1('GreenRO_T1' + name)
    m.AWG_RO_AOM = qt.instruments['PulseAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pts'] = 4
    m.params['repetitions'] =  int(0.02e6/m.params['pts']/2)  #nr of repetitions per cycle
    m.params['nr_of_cycles'] = 9 #75                       # nr of times we read out the qutau
    # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)

    m.params['sweep_name'] = 'free evolution time (ms)'
    m.params['wait_time_repeat_element'] = 100 # in us (a 100 us waiting element is repeated)
    m.params['wait_times'] = np.concatenate( (np.linspace(0,int(1e5), m.params['pts'] - 2), np.linspace(int(2e5), int(3e5),2))) # in us
    # m.params['wait_times'] = np.linspace(0, int(35e3), m.params['pts'])

    # Parameters for analysis
    m.params['sweep_name'] = 'Waiting time (ms)'
    m.params['sweep_pts'] = m.params['wait_times'] * 1e-3

    # The RO
    m.params['do_spatial_optimize'] = False
    m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
    m.params['SSRO_repetitions'] = m.params['total_sync_nr']

    # m.generate_sequence(upload = True)
    missed_syncs, total_syncs = m.measure(debug=False,upload=True)
    return missed_syncs, total_syncs

def Rabi(name):

    m = Green_RO('GreenRO_Rabi'+name)
    m.AWG_RO_AOM = qt.instruments['GreenAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pts'] = 24 #81 #45
    m.params['repetitions'] =  0.5e6/m.params['pts']/2.  #nr of repetitions per cycle
    m.params['nr_of_cycles'] = 2500                       # nr of times we read out the qutau
                                                        # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)
    #About the sweep
    m.params['sweep_name'] = 'Pulse Length [us]'
    m.params['MW_pulse_durations'] = np.linspace(0,2.,m.params['pts'])*1e-6
    m.params['sweep_pts']  = m.params['MW_pulse_durations']*1e6

    # About the MW's
    m.params['mw_frq'] = 2.6980e9 -43e6 ### 43 Mhz for SSBmod
    m.params['MW_modulation_frequency'] = 43e6
    m.params['ssbmod_amplitude']= 0.9#0.45 #0.275 #0.45
    m.params['mw_power']=20
    m.params['MW_modulation_frequencies'] = np.ones(m.params['pts'])*m.params['MW_modulation_frequency']

    # The RO
    m.params['do_spatial_optimize'] = True
    m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
    m.params['SSRO_repetitions'] = m.params['total_sync_nr']

    print 'ro start and stop',m.params['RO_start'],m.params['RO_stop']
    missed_syncs,total_syncs=m.measure(debug=False,upload=True)
    return missed_syncs,total_syncs

def Dark_ESR(name):
    for ssbamp in [0.45]:
        m = Green_RO('GreenRO_DESR'+name+'_ssbAmp_'+str(ssbamp))
        m.AWG_RO_AOM = qt.instruments['GreenAOM']
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
        m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
        m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


        m.params['pts'] = 101
        m.params['repetitions'] =  0.5e6/m.params['pts']/2  #nr of repetitions per cycle
        m.params['nr_of_cycles'] = 20000                       # nr of times we read out the qutau
                                                            # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)
        #About the sweep
        m.params['mw_frq'] = 2.6970e9 - 43e6 #2.6964e9 -43e6 ### 43 Mhz for SSBmod
        m.params['sweep_name'] = 'Frequency [GHz]'
        f_range = 5.3e6
        m.params['MW_pulse_duration'] = 2500e-9#1250e-9#2000e-9
        f_center = 43e6#m.params['MW_modulation_frequency']
        m.params['MW_modulation_frequencies'] = np.linspace(f_center-f_range,f_center+f_range,m.params['pts'])
        m.params['sweep_pts']  = (m.params['MW_modulation_frequencies']+m.params['mw_frq'])*1e-9

        # About the MW's

        m.params['ssbmod_amplitude']= ssbamp
        m.params['mw_power']=19
        m.params['MW_pulse_durations'] = np.ones(m.params['pts'])*m.params['MW_pulse_duration']

        # The RO
        m.params['do_spatial_optimize'] = True
        m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
        m.params['SSRO_repetitions'] = m.params['total_sync_nr']


        missed_syncs,total_syncs=m.measure(debug=False,upload=True)
    return missed_syncs,total_syncs

def Ramsey(name):

    m = GreenRO_Ramsey('GreenRO_Ramsey'+name)
    m.AWG_RO_AOM = qt.instruments['PulseAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    m.params['pts'] =  41
    m.params['repetitions'] =  0.5e6/m.params['pts']/2  #nr of repetitions per cycle
    m.params['nr_of_cycles'] = 200 #75                       # nr of times we read out the qutau
                                                        # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)
    
    # Sweep settings for your conventional Ramsey measurement with an artifical detuning (sweeping phase of second pi/2)
    m.params['sweep_name'] = 'Free Evolution time [us]'
    m.params['detuning']=0e3
    m.params['free_evolution_times'] = np.linspace(2,30,m.params['pts'])*1e-6 # 0 - 20 previously
    m.params['sweep_pts']  = m.params['free_evolution_times']*1e6
    m.params['second_pi2_phases'] = mod(360*m.params['detuning']*m.params['free_evolution_times'] ,360)
    
    #Convenient for calibrations: fixed tau, sweep phase of second pi/2
    sweep_phase=False
    if sweep_phase:
        m.params['sweep_name'] = 'Phase second pi2 [Degrees]'
        m.params['free_evolution_times'] = np.linspace(70,70,m.params['pts'])*1e-6
        m.params['second_pi2_phases'] = np.linspace(0,360,m.params['pts'])
        m.params['sweep_pts']  = m.params['second_pi2_phases']


    # About the MW's
    m.params['mw_power']=15
    #m.params['Square_pi2_amp']=0.04*6
    m.params['MW_modulation_frequencies'] = np.ones(m.params['pts'])*m.params['MW_modulation_frequency']

    
    # The RO
    m.params['do_spatial_optimize'] = True
    m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
    m.params['SSRO_repetitions'] = m.params['total_sync_nr']


    missed_syncs,total_syncs=m.measure(debug=False,upload=True)
    return missed_syncs,total_syncs

def Hahn(name):

    m = GreenRO_Hahn('GreenRO_Hahn'+name)
    m.AWG_RO_AOM = qt.instruments['PulseAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    m.params['pts'] = 18
    m.params['repetitions'] =  0.01e6/m.params['pts']/2  #nr of repetitions per cycle
    m.params['nr_of_cycles'] = 1                       # nr of times we read out the qutau
                                                        # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)
    
    # Sweep settings for your conventional Ramsey measurement with an artifical detuning (sweeping phase of second pi/2)
    m.params['sweep_name'] = 'Free Evolution time [us]'
    m.params['detuning']=0e3
    m.params['free_evolution_times'] = np.concatenate( (np.linspace(1,601,m.params['pts'] - 5), np.linspace(1101, 3101, 5) ), axis = 0 ) *1e-6
    # m.params['free_evolution_times'] = np.linspace(1,51,m.params['pts']) *1e-6
    m.params['sweep_pts']  = m.params['free_evolution_times']*1e6
    m.params['second_pi2_phases'] = mod(360*m.params['detuning']*m.params['free_evolution_times'] ,360)
    
    #Convenient for calibrations: fixed tau, sweep phase of second pi/2
    sweep_phase=False
    if sweep_phase:
        m.params['sweep_name'] = 'Phase second pi2 [Degrees]'
        m.params['free_evolution_times'] = np.linspace(70,70,m.params['pts'])*1e-6
        m.params['second_pi2_phases'] = np.linspace(0,360,m.params['pts'])
        m.params['sweep_pts']  = m.params['second_pi2_phases']

    # About the MW's
    m.params['mw_power']=21
    #m.params['Square_pi2_amp']=0.04*6
    m.params['MW_modulation_frequencies'] = np.ones(m.params['pts'])*m.params['MW_modulation_frequency']

    
    # The RO
    m.params['do_spatial_optimize'] = True
    m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
    m.params['SSRO_repetitions'] = m.params['total_sync_nr']


    missed_syncs,total_syncs=m.measure(debug=False,upload=True)
    return missed_syncs,total_syncs

if __name__ == '__main__':
    GreenAOM.turn_off()
    
    d_syncs,tot_syncs=Rabi(SAMPLE_CFG)
    # d_syncs,tot_syncs=Dark_ESR(SAMPLE_CFG)
    # d_syncs,tot_syncs=Ramsey(SAMPLE_CFG)
    # d_syncs,tot_syncs=Hahn(SAMPLE_CFG)
    # d_syncs,tot_syncs=T1(SAMPLE_CFG)
    # T1(SAMPLE_CFG)
    print d_syncs, tot_syncs
    '''
    for i in np.arange(25):
        d_syncs,tot_syncs=Ramsey(SAMPLE_CFG)
        GreenAOM.set_power(80e-6)
        qt.msleep(10)
        optimiz0r.optimize(dims=['x','y','z','y','x','z'])
        GreenAOM.turn_off()
  
    #for i in np.arange()
    missed_syncs=[]
    failed_msmnts=0
    for i in np.arange(1):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
        d_syncs,tot_syncs=Rabi(SAMPLE_CFG)
        if (d_syncs>1):
            failed_msmnts+=1
        missed_syncs.append(d_syncs)

        print '###############################'
        print 'Total repetitions: ', i+1
        print 'Percentage of missed syncs: ', 100*sum(missed_syncs)/float((i+1)*tot_syncs/2), ' %'
        print 'Percentage of failed msmnts: ', 100*failed_msmnts/float(i+1), ' %'
        print '###############################'
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    #print d_syncs
    '''
import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt


class AdaptivePhaseEstimation(pulsar_msmt.RTMagnetometry):
    mprefix = 'adptv_estimation'

    def generate_sequence(self, upload=True, debug=False):
        # MBI element

        if (self.params['do_MBI']>0):
            Ninit_elt = self._MBI_element()
        else:
            Ninit_elt = self._Ninit_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        FM = pulse.SquarePulse(channel='FM', name='modulation',amplitude=0,length=20e-6)


        fpga_gate = pulselib.MW_pulse(name = 'fpga_gate_pulse', MW_channel='fpga_gate', amplitude = 4.0, length = 10e-9,
            PM_channel = 'MW_pulsemod', PM_risetime = 20*self.params['MW_pulse_mod_risetime'])

        clock_pulse = pulse.clock_train (channel = 'fpga_clock', amplitude = 1, nr_up_points=2, nr_down_points=2, cycles= 1000)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)
        
        # electron manipulation elements
        elts = []
        for i in np.arange(self.params['adptv_steps']):

            
            FM_duration=self.params['FM_delay']+2*self.params['MW_pulse_durations'][i]+self.params['fpga_mw_duration'][i]+self.params['ramsey_time'][i]+1e-6
            for j,FM_amp in enumerate(self.params['FM_amplitude']):               
                #print 'FM_amp', FM_amp
                #print 'FM_duration', FM_duration
                e = element.Element('adpt_step_nr-%(v0)d_MWline%(v1)d'% {"v0":i, "v1":j}, pulsar=qt.pulsar,
                global_time = True)
                last=e.add(pulse.cp(T, length=10e-9),name='T1_%(v0)d_%(v1)d'% {"v0":i, "v1":j})
                #print 'FM_%(v0)d_%(v1)d'% {"v0":i, "v1":j}
                last= e.add(pulse.cp(FM,amplitude=FM_amp,length=FM_duration), name='FM_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last)
                last=e.add(pulse.cp(X, 
                            frequency = self.params['MW_pulse_mod_frqs'][i],
                            amplitude = self.params['MW_pulse_amps'][i],
                            length = self.params['MW_pulse_durations'][i]),name='first_pi2_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last,start=self.params['FM_delay'],refpoint='start')
                
                last=e.add(pulse.cp(T, length=self.params['ramsey_time'][i]),name='tau_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last)
                
                
                if self.params['MW_only_by_awg']:
                    last=e.add(pulse.cp(X,
                            frequency = self.params['MW_pulse_mod_frqs'][i],
                            amplitude = self.params['MW_pulse_amps'][i],
                            length = self.params['MW_pulse_durations'][i],
                            phase = self.params['phase_second_pi2'][i]),name='second_pi2_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last)

                else:    
                    last=e.add(pulse.cp(fpga_gate, amplitude = 4.0, length=self.params['fpga_mw_duration'][i]),name='fpga_gate_pulse_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last)
                    e.add(pulse.cp(clock_pulse, amplitude = 1.0, cycles = 2000+int(0.25e9*self.params['fpga_mw_duration'][i])),name='fpga_clock_%(v0)d_%(v1)d'% {"v0":i, "v1":j},start=-5000e-9,refpulse=last, refpoint='start')
                last='FM_%(v0)d_%(v1)d'% {"v0":i, "v1":j}
                last= e.add(pulse.cp(T, length=10e-9),name='T2_%(v0)d_%(v1)d'% {"v0":i, "v1":j},refpulse=last)    
                if j!=len(self.params['FM_amplitude'])-1:
                    elts.append(e)
                else:
                    last= e.add(T,name='extra_wait',refpulse=last)
                    last=e.add(adwin_sync,name='adwin_sync',refpulse=last)

                    last=e.add(pulse.cp(T, length=100e-9),name='final_wait',refpulse=last)        
                    elts.append(e)

        print 'Elements created...'
        #print 'N-spin init repetitions:', self.params['init_repetitions']
        # sequence
        seq = pulsar.Sequence('Adaptive phase-estimation sequence')
        for i,e in enumerate(elts):
            if (self.params['do_MBI']>0):
                seq.append(name = 'Ninit-dp_%(v0)d' % {"v0":i}, wfname = Ninit_elt.name,
                    trigger_wait = True, goto_target = 'Ninit-dp_%(v0)d' % {"v0":i},
                    jump_target = e.name+'dp_%(v0)d' % {"v0":i})
            #else:
                #print 'No nitrogen initialization'
                #seq.append(name = 'Ninit-dp_%(v0)d-adptvStep_%(v1)d' % {"v0":i, "v1":j}, wfname = Ninit_elt.name,
                #    trigger_wait = True, repetitions=self.params['init_repetitions'])
            if '_MWline0'in e.name:
                seq.append(name = e.name, wfname = e.name,
                trigger_wait = True,repetitions=1)
            else:
                last_mw_pulse_str='MWline'+str(len(self.params['FM_amplitude'])-1)

                if last_mw_pulse_str in e.name:
                    last_adpt_step_str = 'adpt_step_nr-'+str(self.params['adptv_steps']-1)
                    if last_adpt_step_str in e.name:
                        seq.append(name = e.name, wfname = e.name,
                        trigger_wait = False,repetitions=1, goto_target = 'adpt_step_nr-%(v0)d_MWline%(v1)d'% {"v0":i/len(self.params['FM_amplitude']), "v1":0},
                        jump_target = 'adpt_step_nr-%(v0)d_MWline%(v1)d'% {"v0":0, "v1":0})    

                    else:

                        seq.append(name = e.name, wfname = e.name,
                        trigger_wait = False,repetitions=1, goto_target = 'adpt_step_nr-%(v0)d_MWline%(v1)d'% {"v0":i/len(self.params['FM_amplitude']), "v1":0},
                        jump_target = 'adpt_step_nr-%(v0)d_MWline%(v1)d'% {"v0":i/len(self.params['FM_amplitude'])+1, "v1":0})   
                else:
                    seq.append(name = e.name, wfname = e.name,
                    trigger_wait = False,repetitions=1)    
        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, Ninit_elt, *elts , debug=debug,loop=False)
            print 'Done uploading!!'
 
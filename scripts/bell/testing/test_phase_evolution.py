import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import bell
reload(bell)
import sequence as bseq
reload(bseq)
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)

class SweepBellPhase(bell.Bell):
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process
    
    def generate_sequence(self):
 
        self.sweep_bell_seq = pulsar.Sequence('Bell_sweep')
        
        elements = [] 

        for i in range(self.params['pts']):
            if self.params['do_general_sweep'] :
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i]
                #self.params['eom_off_duration'] = self.params['opt_pulse_separation']/4.
            self.params['mw_frq'] = self.params['ms-1_cntr_frq']-self.params['MW_pulse_mod_frequency'] 
            self.params['pulse_pi_amp'] = self.params['IQ_Square_pi_amp']
            self.params['pulse_pi2_amp'] = self.params['IQ_Square_pi2_amp']
            IQ_Square_pi = pulselib.MW_IQmod_pulse('Square pi-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = self.params['MW_pi_duration'],
                    amplitude = self.params['pulse_pi_amp'],
                    phase = self.params['mw_pi_phase'],
                    frequency = self.params['MW_pulse_mod_frequency'],
                    PM_risetime = self.params['MW_pulse_mod_risetime'])
            IQ_Square_pi2 = pulselib.MW_IQmod_pulse('Square pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = self.params['MW_pi2_duration'],
                    amplitude = self.params['pulse_pi2_amp'],
                    phase = self.params['mw_pi2_phase_1'],
                    frequency = self.params['MW_pulse_mod_frequency'],
                    PM_risetime = self.params['MW_pulse_mod_risetime'])
            pulse_pi=IQ_Square_pi
            pulse_pi2=IQ_Square_pi2

            if self.params['setup'] == 'lt4':
                bseq.pulse_defs_lt4(self)
            elif self.params['setup'] == 'lt3':
                bseq.pulse_defs_lt3(self)  

            finished_element = bseq._lt3_sequence_finished_element(self)

            e = element.Element('sweep_el_{}'.format(i), 
                pulsar = qt.pulsar, 
                global_time = True)  
            
            e.add(pulse.cp(self.SP_pulse,
                    amplitude = 0,
                    length = self.joint_params['LDE_element_length']))
            
            #1 SP
            e.add(pulse.cp(self.SP_pulse, 
                    amplitude = 0, 
                    length = self.joint_params['initial_delay']),
                name = 'initial_delay')
            
            e.add(pulse.cp(self.SP_pulse, 
                    length = self.params['LDE_SP_duration'], 
                    amplitude = 1.0), 
                name = 'spinpumping', 
                refpulse = 'initial_delay')

            if self.params['sync_during_LDE'] == 1 :
                e.add(self.sync,
                    refpulse = 'initial_delay')

            for j in range(self.joint_params['opt_pi_pulses']):
                name = 'opt pi {}'.format(j+1)
                refpulse = 'opt pi {}'.format(j) if j > 0 else 'initial_delay'
                start = self.params['opt_pulse_separation'] if j > 0 else self.params['opt_pulse_start']
                refpoint = 'start' if j > 0 else 'end'

                e.add(self.eom_pulse,        
                    name = name, 
                    start = start,
                    refpulse = refpulse,
                    refpoint = refpoint,)

            #4 MW pi/2
            e.add(pulse.cp(pulse_pi2,phase =self.params['mw_pi2_phase_1']), 
                    start = -self.params['MW_opt_puls1_separation'],
                    refpulse = 'opt pi 1', 
                    refpoint = 'start', 
                    refpoint_new = 'end',
                    name = 'MW_first_pi2')
            #5 HHsync

            #8 MW pi 
            e.add(pulse_pi, 
                    start = self.params['MW_1_separation'],
                    refpulse = 'MW_first_pi2',
                    refpoint = 'end', 
                    refpoint_new = 'end', 
                    name='MW_pi')


            # 14 MW pi/2 pulse
            e.add(pulse.cp(pulse_pi2,phase =self.params['mw_pi2_phase_2']), 
                        start = self.params['MW_1_separation'],
                        refpulse = 'MW_pi', 
                        refpoint = 'start', 
                        refpoint_new = 'start',
                        name='MW_final_pi2')
            
            elements.append(e)

            
            self.sweep_bell_seq.append(name = 'Bell sweep {}'.format(i),
                wfname = e.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.joint_params['LDE_attempts_before_CR'])
            
            self.sweep_bell_seq.append(name = 'Bell sweep done {}'.format(i),
                wfname = finished_element.name,
                trigger_wait = False)

        elements.append(finished_element)
        #qt.pulsar.upload(*elements)
        #qt.pulsar.program_sequence(self.sweep_bell_seq)
        qt.pulsar.program_awg(self.sweep_bell_seq,*elements)

    def save(self):
        pulsar_pq.PQPulsarMeasurement.save(self)

    #def run(self,**kw):
    #    pulsar_pq.PQPulsarMeasurement.run(self, **kw)

    def print_measurement_progress(self):
        pulsar_pq.PQPulsarMeasurement.print_measurement_progress(self)

def _setup_params(msmt, setup):
    msmt.params['setup']=setup
    espin_funcs.prepare(msmt)

    
    if not(hasattr(msmt,'joint_params')):
        msmt.joint_params = {}
    import joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        msmt.joint_params[k] = joint_params.joint_params[k]

    if setup == 'lt4' :
        import params_lt4
        reload(params_lt4)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            msmt.params[k] = params_lt4.params_lt4[k]
    elif setup == 'lt3' :
        import params_lt3
        reload(params_lt3)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt3.params_lt3:
            msmt.params[k] = params_lt3.params_lt3[k]
    else:
        print 'Sweep_bell: invalid setup:', setup

    msmt.params['send_AWG_start'] = 1
    msmt.params['sync_during_LDE'] = 1
    msmt.params['wait_for_AWG_done'] = 1
    msmt.params['do_general_sweep']= 1
    msmt.params['trigger_wait'] = 1

def phase_sweep(name):

    print 'setting up the phase sweep'
    m=SweepBellPhase('phase_sweep_'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=1
    m.params['pts']=pts
    m.params['repetitions'] = 1000

    m.params['mw_pi_phase'] = 0
    m.params['mw_pi2_phase_1'] = 0
    m.params['mw_pi2_phase_2'] = 0
    m.params['MW_during_LDE'] = True

    m.joint_params['LDE_element_length'] = 9e-6
    m.joint_params['opt_pi_pulses']      = 2
    m.params['aom_amplitude']            = 0
    m.params['eom_pulse_duration']       = 2e-9
    m.joint_params['LDE_attempts_before_CR'] = 1
    m.params['opt_pulse_separation'] = m.joint_params['opt_pulse_separation']
    do_sweep_aom_power = True
    if do_sweep_aom_power:
        p_aom= qt.instruments['PulseAOM']
        aom_voltage_sweep = np.zeros(pts)
        max_power_aom=p_aom.voltage_to_power(p_aom.get_V_max())
        aom_power_sweep=np.linspace(.001,0.95,pts)*max_power_aom #%power
        for i,p in enumerate(aom_power_sweep):
            aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

        m.params['general_sweep_name'] = 'aom_amplitude' 
        m.params['general_sweep_pts'] = aom_voltage_sweep
        m.params['sweep_name'] = 'aom power (percentage/max_power_aom)' 
        m.params['sweep_pts'] = np.sqrt(aom_power_sweep/max_power_aom)#
    else:
        m.params['general_sweep_name'] = 'mw_pi2_phase_2'#'MW_opt_puls1_separation'#
        m.params['general_sweep_pts'] = np.linspace(0, 360, pts)

    #for the analysis:
        m.params['sweep_name'] = m.params['general_sweep_name']
        m.params['sweep_pts'] = m.params['general_sweep_pts']

    run_sweep(m, th_debug=True, upload_only = True)

def opt_pulse_sweep(name):

    print 'setting up the phase sweep'
    m=SweepBellPhase('phase_sweep_'+name)
    _setup_params(m, setup = qt.current_setup)

    pts=41
    m.params['pts']=pts
    m.params['repetitions'] = 1000

    m.params['mw_pi_phase'] = 0
    m.params['mw_pi2_phase_1'] = 0
    m.params['mw_pi2_phase_2'] = 0
    m.params['MW_during_LDE'] = True

    m.joint_params['LDE_element_length'] = 9e-6
    m.joint_params['opt_pi_pulses']      = 2
    m.params['aom_amplitude']            = 1.
    m.params['eom_pulse_duration']       = 2e-9
    m.joint_params['LDE_attempts_before_CR'] = 1
    m.params['opt_pulse_separation'] = m.joint_params['opt_pulse_separation']

    m.params['general_sweep_name'] = 'opt_pulse_separation'
    m.params['general_sweep_pts'] = np.linspace(400e-9, 600e-9, pts)

    #for the analysis:
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    run_sweep(m, th_debug=True, upload_only = True)

def run_sweep(m, th_debug=False, upload_only = False):
    m.autoconfig()
    m.generate_sequence()
    if upload_only:
        return
    m.setup(debug=th_debug)
    m.run(autoconfig=False, setup=False,debug=th_debug)    
    m.save()  
    m.finish()

if __name__ == '__main__':

    phase_sweep('phase_sweep_wit_opt') 
    #opt_pulse_sweep('test')

import sweep_Bell
reload(sweep_Bell)
# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_pq

class TestMWaftereffect(pulsar_pq.PQPulsarMeasurement):
    """
    General Pi pulse calibration, with a variable delay before a RO in the AWG
    """
    mprefix = 'TestMWaftereffect'

    def autoconfig(self):
        self.params['sequence_wait_time'] = 20
        self.params['RO_voltage_AWG'] = \
                self.AWG_RO_AOM.power_to_voltage(
                        self.params['AWG_RO_power'], controller='sec')
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage(
                        self.params['AWG_SP_power'], controller='sec')
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])

        pulsar_pq.PQPulsarMeasurement.autoconfig(self)


    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_Imod',
            length = 8e-6, amplitude = 0) #XXXX 200e-9

        RO_pulse = pulse.SquarePulse(channel = 'EOM_AOM_Matisse', amplitude = self.params['RO_voltage_AWG'], length=200e-9)#self.joint_params['LDE_RO_duration'])
        SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = self.params['SP_voltage_AWG'], length=5e-6)
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elements = []
        seq = pulsar.Sequence('{} pi calibration'.format(self.params['pulse_type']))
        for i in range(self.params['pts']):
            e = element.Element('pulse-{}'.format(i), pulsar=qt.pulsar)
            e.append(pulse.cp(T,length=100e-9))
            sync_ref = e.append(self.sync)
            e.append(SP_pulse)
            opt_pi_0 = e.add(self.eom_pulse,
                start = 10e-6,
                refpulse = sync_ref,
                refpoint='start')
            opt_pi_1 = e.add(self.eom_pulse,
                start = self.params['opt_sep'][i],
                refpulse = opt_pi_0,
                refpoint='start')
            opt_pi_2 = e.add(self.eom_pulse,
                start = self.params['opt_sep'][i],
                refpulse = opt_pi_1,
                refpoint='start')

            #e.append(T)
                        #e.append(pulse.cp(T,length=self.params['delay_after_MW_lengths'][i]))
            
            e.add(pulse.cp(self.MW_pi2, amplitude = self.params['mw_pi2_amps'][i]),
                start=-self.params['mw_pi2_opt_1_sep'][i],
                refpulse=opt_pi_1,
                refpoint='start',
                refpoint_new='end')
            e.add(self.MW_pi,
                start=-self.params['mw_pi_opt_2_sep'][i],
                refpulse=opt_pi_2,
                refpoint='start',
                refpoint_new='end')

            e.append(T)
            #ro_p = e.append(RO_pulse)
            elements.append(e)

            seq.append(name = e.name, 
                wfname = e.name,
                repetitions = self.params['syncs_per_sweep'],
                trigger_wait = True)
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)


        # sequence
        elements.append(wait_1us)
        elements.append(sync_elt)
        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

def test_mw_aftereffect(name, debug=False):
    m = TestMWaftereffect(name)
    sweep_Bell._setup_params(m, setup = qt.current_setup)

    m.params['pulse_type'] = 'Hermite Bell'
    pts = 7
 
    m.params['Ex_SP_amplitude']=0
    m.params['SP_duration'] = 100

    m.params['pts'] = pts
    m.params['repetitions'] = 2000
   
    m.params['syncs_per_sweep'] = 250
    m.params['mw_pi2_opt_1_sep'] = np.ones(pts)*20e-9#np.linspace(100,1000,pts)*1e-9
    m.params['opt_sep'] = np.ones(pts)*250e-9#np.linspace(250,1000,pts)*1e-9#
    m.params['mw_pi_opt_2_sep'] = np.ones(pts)*20e-9

    m.params['mw_pi2_amps'] = m.params['MW_pi2_amp'] + np.linspace(-0.05, 0.05, pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'mw_pi2_amps [V]'
    m.params['sweep_pts'] = m.params['mw_pi2_amps']*1e9
    m.params['wait_for_AWG_done'] = 1
    m.params['count_marker_channel'] =  1

    m.autoconfig()
    m.generate_sequence(upload=True)
    if not debug:
        m.setup(debug=debug, mw=True)
        m.run(autoconfig=False, setup=False,debug=debug)    
    m.save()  
    m.finish()


if __name__ == '__main__':
    SAMPLE_CFG = qt.exp_params['protocols']['current']
    test_mw_aftereffect(SAMPLE_CFG, debug = False)

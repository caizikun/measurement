"""
This script performs pi pulse calibrations and afterwords aims to RO the individual nitrogen/13C state populations.
By analyzing systematic offsets between the results we aim to create a tool that gives us better understanding of our pulses

NK 2017
"""
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.scripts.espin import espin_funcs
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
from measurement.lib.pulsar import pulselib
execfile(qt.reload_current_setup)


SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

class PiCalibrationWithDESRreadout(pulsar_msmt.GeneralPiCalibration):
    """
    Pretty much the same as the parrent class: GeneralPiCalibration / GeneralPiCalibrationSingleElement
    We add one final pulse that addresses a certain nitrogen state individually.
    """
    def save(self,**kw):

        first = kw.pop('first',True)
        ssro.IntegratedSSRO.save(self, **kw)
        

        if first:
            grp=self.h5basegroup.create_group('pulsar_settings')
            pulsar = kw.pop('pulsar', qt.pulsar)

            for k in pulsar.channels:
                grpc=grp.create_group(k)
                for ck in pulsar.channels[k]:
                    grpc.attrs[ck] = pulsar.channels[k][ck]

            grpa=grp.create_group('AWG_sequence_cfg')
            for k in pulsar.AWG_sequence_cfg:
                grpa.attrs[k] = pulsar.AWG_sequence_cfg[k]


        self.h5data.flush()


    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_Imod',
            length = 15000e-9, amplitude = 0)

        X=kw.get('pulse_pi', None)
        if X==None:
            print 'WARNING: No valid X Pulse'

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        RO_pulse =  pulselib.MW_IQmod_pulse('N_RO_pulse',
                        I_channel = 'MW_Imod',
                        Q_channel = 'MW_Qmod',
                        PM_channel = 'MW_pulsemod',
                        PM_risetime = self.params['MW_pulse_mod_risetime'],
                        frequency = self.params['mw_mod_freq']+self.params['N_RO_frequency_shift'],
                        amplitude = self.params['N_RO_pulse_amp'],
                        length = self.params['N_RO_pulse_duration'])
        
        if type(self.params['multiplicity']) ==int:
            self.params['multiplicity'] = np.ones(self.params['pts'])*self.params['multiplicity']

        if self.params['multiplicity'].all() == 0:
            j = 0

        elements = []
        for i in range(self.params['pts']):
            self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i] 
            e = element.Element('pulse-{}'.format(i), pulsar=qt.pulsar)
            for j in range(int(self.params['multiplicity'][i])):
                e.append(T,
                    pulse.cp(X,
                        amplitude=self.params['fast_pi_amp']
                        ))
            e.append(T)

            if self.params['add_RO_pulse']:
                e.append(pulse.cp(RO_pulse, frequency = self.params['mw_mod_freq']+self.params['N_RO_frequency_shift'],
                                                amplitude = self.params['N_RO_pulse_amp']))

                e.append(T)
            elements.append(e)

        # sequence
        seq = pulsar.Sequence('{} pi calibration'.format(self.params['pulse_shape']))
        for i,e in enumerate(elements):           
            seq.append(name = e.name+'-{}'.format(j), 
                wfname = e.name,
                trigger_wait = True)
            if self.params['delay_reps'] != 0:
                seq.append(name = 'wait-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = self.params['delay_reps'])
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)
        elements.append(wait_1us)
        elements.append(sync_elt)

        # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*elements)


def calibrate_pi_RO_N(name,multiplicity,debug=False,**kw):

    m = PiCalibrationWithDESRreadout(name)

    if qt.current_setup == 'lt3':
        ### formatting is pulse amp, pulse duration, frequency shift
        N_peak_dict = {
            '0'     : [0.000,7e-6,0],
            '1'     : [0.0017,7e-6,+ 876e3/2. + 0.002194e9],
            '2'     : [0.0017,7e-6,- 876e3/2. + 0.002194e9],
            '3'     : [0.0017,7e-6,+ 876e3/2.],
            '4'     : [0.0017,7e-6,- 876e3/2.],
            '5'     : [0.0017,7e-6,+ 876e3/2. - 0.002194e9],
            '6'     : [0.0017,7e-6,- 876e3/2. - 0.002194e9],
        } 

    espin_funcs.prepare(m)
    m.params['wait_for_AWG_done'] = 1
    m.params['AWG_controlled_readout'] = 0
    m.params['delay_reps'] = 0


    ### kws
    calibrate_N_RO = kw.pop('calibrate_N_RO',False)
    
    #### some pulse changes such that we don't interfere with msmt.params.
    f_msp1_cntr = m.params['ms+1_cntr_frq'] 
    mw_mod_frequency = 43e6
    m.params['mw_mod_freq'] = mw_mod_frequency
    m.params['mw_frq'] = f_msp1_cntr - mw_mod_frequency 

    ### initialize a bunch of useful values
    [m.params['N_RO_pulse_amp'], m.params['N_RO_pulse_duration'],  m.params['N_RO_frequency_shift']] = N_peak_dict[str(1)]
    m.MW_pi = pulse.cp(ps.X_pulse(m), phase = 0)


    ### first calibrate all average state populations this is used for ROC purposes
    first = True
    if calibrate_N_RO:
        m.params['repetitions'] = 12000
        m.params['add_RO_pulse'] = True
        pts = 6
        m.params['pts'] = pts
        m.params['general_sweep_pts'] = []
        m.params['general_sweep_name'] = 'N_RO_frequency_shift'
        m.params['multiplicity'] = np.ones(pts)*0
        for i in range(1,pts+1,1):
            m.params['general_sweep_pts'].append(N_peak_dict[str(i)][2])

        m.params['sweep_name'] = 'N/13C dip'
        m.params['sweep_pts'] = np.array(range(1,pts+1,1))
        m.autoconfig()
        m.generate_sequence(upload =True, pulse_pi = m.MW_pi)
        if not debug:
            m.run(autoconfig = False)
            m.save(name = 'n_ro_calibration',first = first)
            first = False


    m.params['add_RO_pulse'] = kw.pop('add_RO_pulse',False)


    ###### here is the actual sweep!
    
    m.params['Hermite_pi_length'] = m.params['Hermite_pi_length'] +10e-9


    pts = 15
    m.params['pts'] = pts
    
    m.params['repetitions'] = 5000 if multiplicity == 1 else 1000
    rng = 0.15 if multiplicity == 1 else 0.06
    # ps.X_pulse(m) ### update pulse params

    m.params['general_sweep_name'] = 'fast_pi_amp'
    m.params['general_sweep_pts'] = np.linspace(0.0,0.95,pts)#m.params['fast_pi_amp'] + np.linspace(-rng, rng, pts)
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    

        # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    
    


    #### get thte correct N_RO_params
    breakst = False
    m.autoconfig()
    for i in range(0,6+1,1):
        breakst = show_stopper()
        if breakst:
            break


        [m.params['N_RO_pulse_amp'], m.params['N_RO_pulse_duration'],  m.params['N_RO_frequency_shift']] = N_peak_dict[str(i)]

        m.generate_sequence(upload = True, pulse_pi = m.MW_pi)
        if not debug:
            m.run(autoconfig = False)
            m.save(name = 'ro_n_dip_'+str(i),first = first)
            first = False

    m.finish()

if __name__ == '__main__':
        calibrate_pi_RO_N(SAMPLE_CFG + 'Pi_and_RO_on_N_13C', calibrate_N_RO = True, 
            multiplicity = 1, debug = False, add_RO_pulse=True)

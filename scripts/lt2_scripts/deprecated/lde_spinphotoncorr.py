# measure spin photon correlations as test before the actual LDE.

# TODO kill measurement sequence
# TODO make sure the awg config is correct
# FIXME there are still some pars over 80! change!

import qt
import numpy as np

import measurement.measurement as meas
from measurement.AWG_HW_sequencer_v2 import Sequence
from measurement.config import awgchannels_lt2 as awgcfg
from measurement.config import adwins as adwincfg

# instruments
adwin_lt2 = qt.instruments['adwin']
# adwin_lt1 = qt.instruments['adwin_lt1']
awg = qt.instruments['AWG']
hharp = qt.instruments['HH_400']
green_aom_lt2 = qt.instruments['GreenAOM']
E_aom_lt2 = qt.instruments['MatisseAOM']
A_aom_lt2 = qt.instruments['NewfocusAOM']
# green_aom_lt1 = qt.instruments['GreenAOM_lt1']
# E_aom_lt1 = qt.instruments['MatisseAOM_lt1']
# A_aom_lt1 = qt.instruments['NewfocusAOM_lt1']

# adwin_mdevice_lt1 = meas.AdwinMeasurementDevice(adwin_lt1, 'adwin_lt1')
adwin_mdevice_lt2 = meas.AdwinMeasurementDevice(adwin_lt2, 'adwin_lt2')

# prepare
awg.set_runmode('CONT')
green_aom_lt2.set_power(0.)
E_aom_lt2.set_power(0.)
A_aom_lt2.set_power(0.)
# green_aom_lt1.set_power(0.)
# E_aom_lt1.set_power(0.)
# A_aom_lt1.set_power(0.)

class LDEMeasurement(meas.Measurement):

    def setup(self, adwin_mdevice_lt2):
        # self.adwin_lt1 = adwin_mdevice_lt1
        self.adwin_lt2 = adwin_mdevice_lt2
        # self.measurement_devices.append(self.adwin_lt1)
        self.measurement_devices.append(self.adwin_lt2)

        # self.adwin_lt1.process_data['lde'] = \
        #         [p for p in adwincfg.config['adwin_lt1_processes']['lde']['par']]

        self.adwin_lt2.process_data['lde'] = \
                [p for p in adwincfg.config['adwin_lt2_processes']['lde']['par']]
        
        
        hharp.start_T3_mode()
        hharp.calibrate()
        hharp.set_Binning(self.binsize_T3)
        
        return True

    def generate_sequence(self, do_program=True):
        self.seq = Sequence('lde')
        seq = self.seq
        
        # channels
        chan_hhsync = 'HH_sync'         # historically PH_start
        chan_hh_ma1 = 'HH_MA1'          # historically PH_sync
        chan_plusync = 'PLU_gate'
        
        chan_alaser = 'AOM_Newfocus'
        chan_eom = 'EOM_Matisse'
        chan_eom_aom = 'EOM_AOM_Matisse'
        
        chan_mw_pm = 'MW_pulsemod'
        chan_mwI_lt2 = 'MW_Imod'
        chan_mwQ_lt2 = 'MW_Qmod'
        chan_mwI_lt1 = 'MW_Imod_lt1'
        chan_mwQ_lt1 = 'MW_Qmod_lt1'

        # TODO study the current AWG configuration, then adapt this
        awgcfg.configure_sequence(self.seq, 'hydraharp', 'mw',
                LDE = { 
                    chan_eom_aom: { 'high' : self.eom_aom_amplitude },
                    chan_alaser: { 'high' : self.A_SP_amplitude, }
                    },
                )
        seq.add_element('lde', goto_target='idle', 
                repetitions=self.max_LDE_attempts, event_jump_target='idle',
                trigger_wait=True)
                
        # 1: spin pumping
        seq.add_pulse('initialdelay', chan_alaser, 'lde',
                start = 0, duration = 10, amplitude=0, )
        seq.add_pulse('spinpumping', chan_alaser, 'lde', 
                start = 0, duration = self.SP_duration,
                start_reference='initialdelay',
                link_start_to='end', amplitude=1)

        # 2: Pi/2 pulses on both spins
        seq.add_pulse('pi/2-1 lt2', chan_mwI_lt2, 'lde',
                duration = self.pi2_lt2_duration,
                amplitude = self.pi2_lt2_amplitude,
                start_reference = 'spinpumping',
                start = self.wait_after_SP, 
                link_start_to = 'end' )
        seq.add_pulse('pi/2-1 lt1', chan_mwI_lt1, 'lde',
                duration = self.pi2_lt1_duration,
                amplitude = self.pi2_lt1_amplitude,
                start_reference = 'pi/2-1 lt2',
                start = (self.pi2_lt2_duration-self.pi2_lt1_duration)/2,
                link_start_to = 'start' )
        
        seq.add_pulse('pi/2-1 pm', chan_mw_pm, 'lde',
                amplitude = self.MW_pulsemod_amplitude,
                duration = max(self.pi2_lt2_duration+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pi2_lt1_duration+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pi2_lt2_duration-self.pi2_lt1_duration)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pi/2-1 lt2',
                link_start_to = 'start' )

        # 3a: optical pi-pulse no 1
        i = 1
        last = 'pi/2-1 pm'
        
        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.wait_after_pi2, duration = 50, 
                amplitude = 2.0, start_reference = last,  
                link_start_to = 'end')
        last = 'start'+str(i)

        seq.add_pulse('mrkr'+str(i), chan_hh_ma1, 'lde',
                start=-20, duration=50,
                amplitude=2.0, start_reference=last,
                link_start_to='start')

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = m.aom_start, duration = m.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_off_amplitude,
                start = m.eom_start, duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_pulse_amplitude - m.eom_off_amplitude,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset, duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot1,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot2,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration + \
                        m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration, 
                duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_pulse_amplitude + m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset, 
                duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot1, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot2, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration + m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_overshoot2_comp'+str(i)
        last = 'EOM_pulse'+str(i)

        # 3b: add pre-sync pulses for the HH
        for j in range(self.presync_pulses):
            seq.add_pulse('presync'+str(j),  chan_hhsync, 'lde',         
                    start = -(j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = 2.0, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 3c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )


        # 4: spin pi pulses
        seq.add_pulse('pi lt2', chan_mwI_lt2, 'lde',
                duration = self.pi_lt2_duration,
                amplitude = self.pi_lt2_amplitude,
                start_reference = last,
                start = self.wait_after_opt_pi, 
                link_start_to = 'start' )
        seq.add_pulse('pi lt1', chan_mwI_lt1, 'lde',
                duration = self.pi_lt1_duration,
                amplitude = self.pi_lt1_amplitude,
                start_reference = 'pi lt2',
                start = (self.pi_lt2_duration-self.pi_lt1_duration)/2,
                link_start_to = 'start' )
        seq.add_pulse('pi pm', chan_mw_pm, 'lde',
                amplitude = self.MW_pulsemod_amplitude,
                duration = max(self.pi_lt2_duration+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.pi_lt1_duration+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.pi_lt2_duration-self.pi_lt1_duration)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'pi lt2',
                link_start_to = 'start')

        # 5a: optical pi-pulse no2
        i = 2

        seq.add_pulse('start'+str(i),  chan_hhsync, 'lde',         
                start = self.opt_pi_separation, duration = 50, 
                amplitude = 2.0, start_reference = 'start'+str(i-1),  
                link_start_to = 'start') 
        last = 'start'+str(i)

        seq.add_pulse('start'+str(i)+'delay',  chan_hhsync, 'lde', 
                start = 0, duration = 50, amplitude = 0,
                start_reference = last,  link_start_to = 'end') 
        last = 'start'+str(i)+'delay'

        seq.add_pulse('AOM'+str(i),  chan_eom_aom, 'lde', 
                start = m.aom_start, duration = m.aom_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_off_amplitude,
                start = m.eom_start, duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_pulse_amplitude - m.eom_off_amplitude,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset, duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot1,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2'+str(i),  chan_eom, 'lde', 
                amplitude = m.eom_overshoot2,
                start = m.eom_start + m.eom_off_duration/2 + \
                        m.eom_pulse_offset + m.eom_pulse_duration + \
                        m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_off_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration, 
                duration = m.eom_off_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_pulse_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_pulse_amplitude + m.eom_off_amplitude,
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset, 
                duration = m.eom_pulse_duration, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot1_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot1, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration, 
                duration = m.eom_overshoot_duration1, 
                start_reference = last, link_start_to = 'start')

        seq.add_pulse('EOM_overshoot2_comp'+str(i),  chan_eom, 'lde', 
                amplitude = -m.eom_overshoot2, 
                start = m.eom_start+m.eom_off_duration + \
                        int(m.eom_off_duration/2) + m.eom_pulse_offset + \
                        m.eom_pulse_duration + m.eom_overshoot_duration1, 
                duration = m.eom_overshoot_duration2, 
                start_reference = last, link_start_to = 'start')
        last = 'EOM_overshoot2_comp'+str(i)

        # 5b: add post-sync pulses for the HH
        for j in range(self.postsync_pulses):
            seq.add_pulse('postsync'+str(j),  chan_hhsync, 'lde',         
                    start = (j+1)*self.opt_pi_separation, duration = 50, 
                    amplitude = 2.0, start_reference = 'start'+str(i),  
                    link_start_to = 'start')

        # 5c: add PLU gate
        seq.add_pulse('plu-gate'+str(i), chan_plusync, 'lde',
                start = 0,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'EOM_pulse'+str(i),
                link_start_to = 'end' )

        # 5d: two additional PLU gates
        seq.add_pulse('plu-gate3', chan_plusync, 'lde',
                start = self.plu_3_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')
        seq.add_pulse('plu-gate4', chan_plusync, 'lde',
                start = self.plu_4_delay,
                duration = self.plu_gate_duration,
                amplitude = 2.0,
                start_reference = 'plu-gate2',
                link_start_to = 'end')

        # 6: basis rotation
        if m.basis_rot:
            Iamplt1 = self.basis_rot_I_amplitude_lt1
            Qamplt1 = self.basis_rot_Q_amplitude_lt1
            Iamplt2 = self.basis_rot_I_amplitude_lt2
            Qamplt2 = self.basis_rot_Q_amplitude_lt2
            PMamp = self.MW_pulsemod_amplitude
        else:
            Iamplt1=Qamplt1=Iamplt2=Qamplt2=PMamp=0

        seq.add_pulse('basis rot lt2 I', chan_mwI_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Iamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi, 
                link_start_to = 'end' )
        seq.add_pulse('basis rot lt2 Q', chan_mwQ_lt2, 'lde',
                duration = self.basis_rot_duration_lt2,
                amplitude = Qamplt2,
                start_reference = last,
                start = self.wait_after_opt_pi2, 
                link_start_to = 'end' )        

        seq.add_pulse('basis rot lt1 I', chan_mwI_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Iamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )
        seq.add_pulse('basis rot lt1 Q', chan_mwQ_lt1, 'lde',
                duration = self.basis_rot_duration_lt1,
                amplitude = Qamplt1,
                start_reference = 'basis rot lt2 I',
                start = (self.basis_rot_duration_lt2-\
                        self.basis_rot_duration_lt1)/2,
                link_start_to = 'start' )

        seq.add_pulse('basis rot pm', chan_mw_pm, 'lde',
                amplitude = PMamp,
                duration = max(self.basis_rot_duration_lt2+\
                        2*self.MW_pulsemod_risetime_lt2,
                    self.basis_rot_duration_lt1+\
                            2*self.MW_pulsemod_risetime_lt1),
                start = min(-self.MW_pulsemod_risetime_lt2,
                    (self.basis_rot_duration_lt2-\
                            self.basis_rot_duration_lt1)/2 - \
                            self.MW_pulsemod_risetime_lt1),
                start_reference = 'basis rot lt2 I',
                link_start_to = 'start')
        
        # 7: final delay
        seq.add_pulse('final delay', chan_hhsync, 'lde',
                amplitude = 0,
                duration = self.finaldelay,
                start = 0,
                start_reference = 'postsync'+str(self.postsync_pulses-1),
                link_start_to = 'end' )

        # idle element
        seq.add_element('idle', goto_target='lde')
        seq.add_pulse('empty', chan_alaser, 'idle', start=0, duration = 1000, 
            amplitude = 0)

        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()        
        
        return seq


    def measure(self, adwin_lt2_params={}, adwin_lt1_params={}):
        # self.adwin_lt1.process_params = adwin_lt1_params
        self.adwin_lt2.process_params = adwin_lt2_params

        awg.set_runmode('SEQ')
        awg.start()
        hharp.StartMeas(self.measurement_time)
        # adwin_lt1.start_lde(**adwin_lt1_params)
        adwin_lt2.start_lde(**adwin_lt2_params)

        ch0_events, ch1_events, markers = hharp.get_T3_pulsed_events(
                sync_period = 200,
                range_sync = 500,
                start_ch0 = 0,
                start_ch1 = 0,
                max_pulses = 2,
                save_markers = [2])
        
        adwin_lt2.stop_lde()
        # adwin_lt1.stop_lde()
        awg.stop()
        qt.msleep(0.1)
        awg.set_runmode('CONT')        

        return ch0_events, ch1_events, markers

    def get_adwin_data(self, noof_readouts=10000, crhist_length=100):
        # a1_crhist_first = self.adwin_lt1.get(
        #         'CR_hist_first', start=1, length=crhist_length)
        # a1_crhist = self.adwin_lt1.get(
        #         'CR_hist', start=1, length=crhist_length)
        # a1_ssro = self.adwin_lt1.get(
        #         'SSRO_counts', start=1, length=noof_readouts)
        # a1_cr = self.adwin_lt1.get(
        #         'CR_before_SSRO_counts', start=1, length=noof_readouts)
        a2_crhist_first = self.adwin_lt2.get(
                'CR_hist_first', start=1, length=crhist_length)
        a2_crhist = self.adwin_lt2.get(
                'CR_hist', start=1, length=crhist_length)
        a2_ssro = self.adwin_lt2.get(
                'SSRO_counts', start=1, length=noof_readouts)
        a2_cr = self.adwin_lt2.get(
                'CR_before_SSRO_counts', start=1, length=noof_readouts)

        return {
                # 'adwin_lt1_CRhist_first' : a1_crhist_first,
                # 'adwin_lt1_CRhist' : a1_crhist,
                # 'adwin_lt1_SSRO'   : a1_ssro,
                # 'adwin_lt1_CR'     : a1_cr,
                'adwin_lt2_CRhist_first' : a2_crhist_first,
                'adwin_lt2_CRhist' : a2_crhist,
                'adwin_lt2_SSRO'   : a2_ssro,
                'adwin_lt2_CR'     : a2_cr,
                }

    def save(self, **kw):
        self.save_dataset(data=kw, plot=False)

        # TODO here: plotting stuff and transferring to website
        #

    def optimize(self):
        pass

    def end(self):
        pass


# intial setup
m = LDEMeasurement('test1', 'LDESpinPhotonCorr')

### measurement parameters

# laser pulses controlled by adwin
m.green_repump_power        = 200e-6
m.green_off_voltage         = 0
m.Ex_CR_power               = 5e-9
m.A_CR_power                = 5e-9
m.Ex_RO_power               = 5e-9
m.A_RO_power                = 0

# general LDE
m.measurement_time          = 60 * 15
m.max_LDE_attempts          = 100
m.finaldelay                = 0     # after last postsync pulse

# spin pumping
A_aom_lt2.set_cur_controller('AWG')
# A_aom_lt1.set_cur_controller('AWG')
m.A_SP_power                = 15e-9
m.A_SP_amplitude            = A_aom_lt2.power_to_voltage(m.A_SP_power)
m.SP_duration               = 2000
m.wait_after_SP             = 100

# spin manipulation
m.MW_pulsemod_risetime_lt2  = 10
m.MW_pulsemod_risetime_lt1  = 10
m.MW_pulsemod_amplitude     = 1.0
m.pi2_lt2_duration          = 25
m.pi2_lt1_duration          = 25
m.pi2_lt2_amplitude         = 1.0
m.pi2_lt1_amplitude         = 1.0
m.wait_after_pi2            = 0
m.pi_lt2_duration           = 50
m.pi_lt1_duration           = 50
m.pi_lt2_amplitude          = 1.0
m.pi_lt1_amplitude          = 1.0
m.basis_rot                 = False
m.basis_rot_I_amplitude_lt1 = 1.0
m.basis_rot_Q_amplitude_lt1 = 0.0
m.basis_rot_I_amplitude_lt2 = 1.0
m.basis_rot_Q_amplitude_lt2 = 0.0
m.basis_rot_duration_lt1    = 25
m.basis_rot_duration_lt2    = 25

# optical pi-pulses
m.eom_aom_amplitude         = 1.0
m.eom_off_amplitude         = -.25
m.eom_pulse_amplitude       = 1.2
m.eom_overshoot_duration1   = 10
m.eom_overshoot1            = -0.03
m.eom_overshoot_duration2   = 10
m.eom_overshoot2            = -0.0
m.eom_start                 = 40
m.eom_off_duration          = 70
m.eom_pulse_duration        = 2
m.eom_pulse_offset          = 0
m.pulse_start               = m.eom_start + m.eom_off_duration/2 + \
        m.eom_pulse_offset
m.aom_start                 = m.pulse_start - 35 -45 #subtract aom rise time
m.aom_duration              = 2*23+m.eom_pulse_duration #30
m.rabi_cycle_duration       = 2*m.eom_off_duration
m.wait_after_opt_pi         = 0
m.wait_after_opt_pi2        = 0
m.opt_pi_separation         = 2*m.eom_off_duration

# HH settings
m.presync_pulses            = 10
m.postsync_pulses           = 10
m.binsize_T3                = 8

# PLU pulses
m.plu_gate_duration         = 50
m.plu_3_delay               = 100   # (ns, after 2nd plu pulse)
m.plu_4_delay               = 200   # (ns, after 2nd plu pulse)

# adwin process parameters
adpar = {}
adpar['counter_channel'] = 1
adpar['green_laser_DAC_channel']    = adwin_lt2.get_dac_channels()['green_aom']
adpar['Ex_laser_DAC_channel']       = adwin_lt2.get_dac_channels()['matisse_aom']
adpar['A_laser_DAC_channel']        = adwin_lt2.get_dac_channels()['newfocus_aom']
adpar['CR_duration']                = 100
adpar['CR_preselect']               = 10
adpar['CR_probe']                   = 10
adpar['green_repump_duration']      = 6
adpar['wait_before_SSRO']           = 1
adpar['SSRO_duration']              = 20
adpar['max_LDE_duration']           = 1000 # TODO depends on sequence length!
adpar['AWG_start_DO_channel']       = 1
adpar['PLU_arm_DO_channel']         = 18 # TODO figure out!
adpar['remote_CR_DO_channel']       = 16
adpar['remote_CR_done_DI_bit']      = 2**8
adpar['remote_CR_SSRO_DO_channel']  = 17
adpar['PLU_success_DI_bit']         = 2**9 # TODO figure out

green_aom_lt2.set_cur_controller('ADWIN')
E_aom_lt2.set_cur_controller('ADWIN')
A_aom_lt2.set_cur_controller('ADWIN')
adpar['green_repump_voltage']       = green_aom_lt2.power_to_voltage(
        m.green_repump_power)
adpar['green_off_voltage']          = m.green_off_voltage
adpar['Ex_CR_voltage']              = E_aom_lt2.power_to_voltage(
        m.Ex_CR_power)
adpar['A_CR_voltage']               = A_aom_lt2.power_to_voltage(
        m.A_CR_power)
adpar['Ex_RO_voltage']              = E_aom_lt2.power_to_voltage(
        m.Ex_RO_power)
adpar['A_RO_voltage']               = 0

# remote adwin process parameters
# adpar_lt1 = {}
# adpar_lt1['counter_channel'] = 1
# adpar_lt1['green_laser_DAC_channel']    = adwin_lt1.get_dac_channels()['green_aom']
# adpar_lt1['Ex_laser_DAC_channel']       = adwin_lt1.get_dac_channels()['matisse_aom']
# adpar_lt1['A_laser_DAC_channel']        = adwin_lt1.get_dac_channels()['newfocus_aom']
# adpar_lt1['CR_duration']                = 100
# adpar_lt1['CR_preselect']               = 10
# adpar_lt1['CR_probe']                   = 10
# adpar_lt1['green_repump_duration']      = 6
# adpar_lt1['remote_CR_DI_channel']       = 10
# adpar_lt1['remote_CR_done_DO_channel']  = 1
# adpar_lt1['remote_SSRO_DI_channel']     = 9
# adpar_lt1['SSRO_duration']              = 20
# 
# green_aom_lt1.set_cur_controller('ADWIN')
# E_aom_lt1.set_cur_controller('ADWIN')
# A_aom_lt1.set_cur_controller('ADWIN')
# adpar_lt1['green_repump_voltage']       = green_aom_lt1.power_to_voltage(
#         m.green_repump_power)
# adpar_lt1['green_off_voltage']          = m.green_off_voltage
# adpar_lt1['Ex_CR_voltage']              = E_aom_lt1.power_to_voltage(
#         m.Ex_CR_power)
# adpar_lt1['A_CR_voltage']               = A_aom_lt1.power_to_voltage(
#         m.A_CR_power)
# adpar_lt1['Ex_RO_voltage']              = E_aom_lt1.power_to_voltage(
#         m.Ex_RO_power)
# adpar_lt1['A_RO_voltage']               = 0


#### actual code
m.generate_sequence()


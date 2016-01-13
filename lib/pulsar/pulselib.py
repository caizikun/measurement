import numpy as np
import scipy.special as ssp
import pulse; 

### Basic multichannel pulses

class MW_pulse(pulse.Pulse):
    def __init__(self, name, MW_channel, PM_channel, **kw):
        pulse.Pulse.__init__(self, name)

        self.MW_channel = MW_channel
        self.PM_channel = PM_channel
        self.channels = [MW_channel, PM_channel]
        self.second_MW_channel = kw.pop('second_MW_channel', None)
        
        self.amplitude = kw.pop('amplitude', 0.1)
        self.length = kw.pop('length', 1e-6)
        self.PM_risetime = kw.pop('PM_risetime', 0)

        if self.second_MW_channel != None:
            self.channels.append(self.second_MW_channel)
            self.second_channel_amp_factor = kw.pop('second_channel_amp_factor', 1.)

        self.pulse_length = self.length
        self.length += 2*self.PM_risetime

        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime

    def __call__(self, **kw):
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length-2*self.PM_risetime) + \
            2*self.PM_risetime
        self.pulse_length = self.length-2*self.PM_risetime
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:  
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1]
            wf = np.zeros(len(tvals))
            wf[idx0:idx1] += self.amplitude*self.second_channel_amp_factor if chan == self.second_MW_channel else self.amplitude
            return wf


class MW_IQmod_pulse(pulse.Pulse):
    # Updated 14-3-15 by MAB to implement MW Switch on lt2
    def __init__(self, name, I_channel, Q_channel, PM_channel, **kw):
        pulse.Pulse.__init__(self, name)


        self.I_channel = I_channel
        self.Q_channel = Q_channel
        self.PM_channel = PM_channel
        self.channels = [I_channel, Q_channel, PM_channel]
        # self.Sw_channel = 'MW_switch'
        # self.channels = [I_channel, Q_channel, PM_channel, 'MW_switch']
        # For implementation of MW Switch (has been implemented on lt2)
        if 'Sw_channel' in kw:
            self.Sw_channel = kw['Sw_channel']
            self.channels.append(self.Sw_channel)


        self.frequency = kw.pop('frequency', 1e6)
        self.amplitude = kw.pop('amplitude', 0.1)
        self.length = kw.pop('length', 1e-6)
        self.phase = kw.pop('phase', 0.)
        self.PM_risetime = kw.pop('PM_risetime', 0)
        # self.Sw_risetime = kw.pop('Sw_risetime', 100e-9)
        self.Sw_risetime = kw.pop('Sw_risetime', 0)

        self.phaselock = kw.pop('phaselock', True)
        self.risetime = kw.pop('risetime', max(self.PM_risetime,self.Sw_risetime))

        self.length += 2*self.risetime
        self.start_offset = self.risetime
        self.stop_offset = self.risetime


    def __call__(self, **kw):
        self.frequency = kw.pop('frequency', self.frequency)
        self.amplitude = kw.pop('amplitude', self.amplitude)
        self.length = kw.pop('length', self.length-2*self.risetime) + \
            2*self.risetime
        self.phase = kw.pop('phase', self.phase)
        self.phaselock = kw.pop('phaselock', self.phaselock)

        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            idx0 = np.where(tvals >= tvals[0] + self.risetime - self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.risetime + self.PM_risetime)[0][-1]

            wf = np.zeros(len(tvals))
            wf[idx0:idx1] = np.ones(idx1 - idx0)

            return wf

        elif hasattr(self,'Sw_channel') and chan == self.Sw_channel: 
        # elif chan == self.Sw_channel:
            idx0 = np.where(tvals >= tvals[0] + self.risetime - self.Sw_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.risetime + self.Sw_risetime)[0][-1]
            
            wf = np.zeros(len(tvals))
            wf[idx0:idx1] = np.ones(idx1 - idx0)

            return wf

        else:  
            idx0 = np.where(tvals >= tvals[0] + self.risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.risetime)[0][-1]

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

                print self.name, tvals[0]

            if chan == self.I_channel:
                wf[idx0:idx1] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[idx0:idx1] + self.phase/360.))

            if chan == self.Q_channel:
                wf[idx0:idx1] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[idx0:idx1] + self.phase/360.))

            return wf

# # Uncomment to use without switch
# class MW_IQmod_pulse(pulse.Pulse):
#     def __init__(self, name, I_channel, Q_channel, PM_channel, **kw):
#         pulse.Pulse.__init__(self, name)

#         self.I_channel = I_channel
#         self.Q_channel = Q_channel
#         self.PM_channel = PM_channel
#         self.channels = [I_channel, Q_channel, PM_channel]

#         self.frequency = kw.pop('frequency', 1e6)
#         self.amplitude = kw.pop('amplitude', 0.1)
#         self.length = kw.pop('length', 1e-6)
#         self.phase = kw.pop('phase', 0.)
#         self.PM_risetime = kw.pop('PM_risetime', 0)
#         self.phaselock = kw.pop('phaselock', True)

#         self.length += 2*self.PM_risetime
#         self.start_offset = self.PM_risetime
#         self.stop_offset = self.PM_risetime


#    def __call__(self, **kw):
#        self.frequency = kw.pop('frequency', self.frequency)
#        self.amplitude = kw.pop('amplitude', self.amplitude)
# 
#        self.length = kw.pop('length', self.length-2*self.PM_risetime) + \
#            2*self.PM_risetime
#        self.phase = kw.pop('phase', self.phase)
#        self.phaselock = kw.pop('phaselock', self.phaselock)
#
#
#        return self

#     def chan_wf(self, chan, tvals):
#         if chan == self.PM_channel:
#             return np.ones(len(tvals))

#         else:  
#             idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
#             idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1]

#             wf = np.zeros(len(tvals))
            
#             # in this case we start the wave with zero phase at the effective start time
#             # (up to the specified phase)
#             if not self.phaselock:
#                 tvals = tvals.copy() - tvals[idx0]

#                 print self.name, tvals[0]

#             if chan == self.I_channel:
#                 wf[idx0:idx1] += self.amplitude * np.cos(2 * np.pi * \
#                     (self.frequency * tvals[idx0:idx1] + self.phase/360.))
            # print 'phase =', self.phase

#             if chan == self.Q_channel:
#                 wf[idx0:idx1] += self.amplitude * np.sin(2 * np.pi * \
#                     (self.frequency * tvals[idx0:idx1] + self.phase/360.))

#             return wf

# class MW_IQmod_pulse
class CORPSE_pulse:

    def __init__(self, name, **kw):

        self.eff_rotation_angle = kw.pop('eff_rotation_angle', 0)
        self.rabi_frequency = kw.pop('rabi_frequency', 0)
        self.eff_rotation_angle_rad = self.eff_rotation_angle/360.*2*np.pi #np.sin expects radians

        self.rotation_integers = kw.pop('rotation_integers', [1,1,0])

        self.length_1,  self.length_2,  self.length_3 = self._get_lengths()
      
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)

        self.length = self.length_1 + self.length_2 + self.length_3 + \
            2*self.pulse_delay + 2*self.PM_risetime

    def __call__(self, **kw):
        self.eff_rotation_angle = kw.pop('eff_rotation_angle', self.eff_rotation_angle)
        self.rabi_frequency = kw.pop('rabi_frequency', self.rabi_frequency)
        self.eff_rotation_angle_rad = self.eff_rotation_angle/360.*2*np.pi #np.sin expects radians

        self.length_1,  self.length_2,  self.length_3 = self._get_lengths()

        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)

        self.length = self.length_1 + self.length_2 + self.length_3 + \
            2*self.pulse_delay + 2*self.PM_risetime

    def _get_lengths(self):
        rotation_angle_1 = 2*np.pi*self.rotation_integers[0] + self.eff_rotation_angle_rad/2 - np.arcsin(np.sin(self.eff_rotation_angle_rad/2)/2)
        rotation_angle_2 = 2*np.pi*self.rotation_integers[1] - 2 * np.arcsin(np.sin(self.eff_rotation_angle_rad/2)/2)
        rotation_angle_3 = 2*np.pi*self.rotation_integers[2] + self.eff_rotation_angle_rad/2 - np.arcsin(np.sin(self.eff_rotation_angle_rad/2)/2)

        length_1 = rotation_angle_1/(2*np.pi)/self.rabi_frequency # 420 for pi
        length_2 = rotation_angle_2/(2*np.pi)/self.rabi_frequency # 300 for pi
        length_3 = rotation_angle_3/(2*np.pi)/self.rabi_frequency # 60 for pi

        return length_1, length_2, length_3

    def _get_starts_ends(self,tvals):

        start_1 = np.where(tvals <= (tvals[0] + self.PM_risetime))[0][-1]
        end_1 = np.where(tvals <= (tvals[0] + self.length_1 + self.PM_risetime))[0][-1]
        start_2 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_1 + \
            self.pulse_delay))[0][-1]
        end_2 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_1 + \
            self.pulse_delay + self.length_2))[0][-1]
        start_3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_1 + \
            self.pulse_delay + self.length_2 + self.pulse_delay))[0][-1]
        end_3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_1 + \
            self.pulse_delay + self.length_2 + self.pulse_delay + \
            self.length_3))[0][-1]

        return start_1, end_1, start_2, end_2, start_3, end_3 

### Shaped pulses
class IQ_CORPSE_pulse(MW_IQmod_pulse, CORPSE_pulse):
    
     # this is between the driving pulses (not PM)
    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg, **kw)
        CORPSE_pulse.__init__(self, *arg, **kw)
   
    def __call__(self, **kw):
        MW_IQmod_pulse.__call__(self, **kw)
        CORPSE_pulse.__call__(self, **kw)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]

            start_1, end_1, start_2, end_2, start_3, end_3  = self._get_starts_ends(tvals)

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

            if chan == self.I_channel:
                wf[start_1:end_1] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_1:end_1] + self.phase/360.))
                wf[start_2:end_2] -= self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_2:end_2] + self.phase/360.))
                wf[start_3:end_3] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_3:end_3] + self.phase/360.))

            if chan == self.Q_channel:
                wf[start_1:end_1] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_1:end_1] + self.phase/360.))
                wf[start_2:end_2] -= self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_2:end_2] + self.phase/360.))
                wf[start_3:end_3] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_3:end_3] + self.phase/360.))

            return wf

class IQ_CORPSE_pi2_pulse(MW_IQmod_pulse):
    # this is between the driving pulses (not PM)

    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg, **kw)

        self.length_24p3 = kw.pop('length_24p3', 0)
        self.length_m318p6 = kw.pop('length_m318p6', 0)
        self.length_384p3 = kw.pop('length_384p3', 0)
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)


        self.length = self.length_24p3 + self.length_m318p6 + self.length_384p3 + \
            2*self.pulse_delay + 2*self.PM_risetime

        self.start_offset = self.PM_risetime
        self.stop_offset = self.PM_risetime

    def __call__(self, **kw):
        MW_IQmod_pulse.__call__(self, **kw)

        self.length_24p3 = kw.pop('length_24p3', self.length_24p3)
        self.length_m318p6 = kw.pop('length_m318p6', self.length_m318p6)
        self.length_384p3 = kw.pop('length_384p3', self.length_384p3)
        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)

        self.length = self.length_24p3 + self.length_m318p6 + self.length_384p3 + \
            2*self.pulse_delay + 2*self.PM_risetime

        return self

    def chan_wf(self, chan, tvals):
        
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:
            idx0 = np.where(tvals >= tvals[0] + self.PM_risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.PM_risetime)[0][-1] + 1

            start_384p3 = np.where(tvals <= (tvals[0] + self.PM_risetime))[0][-1]
            end_384p3 = np.where(tvals <= (tvals[0] + self.length_384p3 + self.PM_risetime))[0][-1]
            start_m318p6 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay))[0][-1]
            end_m318p6 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6))[0][-1]
            start_24p3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6 + self.pulse_delay))[0][-1]
            end_24p3 = np.where(tvals <= (tvals[0] + self.PM_risetime + self.length_384p3 + \
                self.pulse_delay + self.length_m318p6 + self.pulse_delay + \
                self.length_24p3))[0][-1]

            wf = np.zeros(len(tvals))
            
            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

                print self.name, tvals[0]

            if chan == self.I_channel:
                wf[start_384p3:end_384p3] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_384p3:end_384p3] + self.phase/360.))
                wf[start_m318p6:end_m318p6] -= self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_m318p6:end_m318p6] + self.phase/360.))
                wf[start_24p3:end_24p3] += self.amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_24p3:end_24p3] + self.phase/360.))

            if chan == self.Q_channel:
                wf[start_384p3:end_384p3] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_384p3:end_384p3] + self.phase/360.))
                wf[start_m318p6:end_m318p6] -= self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_m318p6:end_m318p6] + self.phase/360.))
                wf[start_24p3:end_24p3] += self.amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_24p3:end_24p3] + self.phase/360.))

            return wf

class composite_pi2_pi_pi2_pulse_IQ(MW_IQmod_pulse):
    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg,amplitude=1., **kw)

        self.length_p1 = kw.pop('length_p1', 0)
        self.length_p2 = kw.pop('length_p2', 0)
        self.length_p3 = kw.pop('length_p3', 0) 
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)
        self.length = self.length_p1 + self.length_p2 + self.length_p3 + self.pulse_delay*2 +self.risetime*2

        self.env_p1_amplitude = kw.pop('amplitude_p1', 0.1)
        self.env_p2_amplitude = kw.pop('amplitude_p2', 0.1)
        self.env_p3_amplitude = kw.pop('amplitude_p3', 0.1)
        self.phase_p1 = kw.pop('phase_p1',0)
        self.phase_p2 = kw.pop('phase_p2',0)
        self.phase_p3 = kw.pop('phase_p3',0)

        self.start_offset = self.risetime
        self.stop_offset = self.risetime

    def __call__(self, *arg, **kw):
        MW_IQmod_pulse.__call__(self, *arg,amplitude=1., **kw)

        self.length_p1 = kw.pop('length_p1', self.length_p1)
        self.length_p2 = kw.pop('length_p2', self.length_p2)
        self.length_p3 = kw.pop('length_p3', self.length_p3) 
        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)
        self.length = self.length_p1 + self.length_p2 + self.length_p3 + self.pulse_delay*2 +self.risetime*2

        self.env_p1_amplitude = kw.pop('amplitude_p1', self.env_p1_amplitude)
        self.env_p2_amplitude = kw.pop('amplitude_p2', self.env_p2_amplitude)
        self.env_p3_amplitude = kw.pop('amplitude_p3', self.env_p3_amplitude)
        self.phase_p1 = kw.pop('phase_p1',self.phase_p1)
        self.phase_p2 = kw.pop('phase_p2',self.phase_p2)
        self.phase_p3 = kw.pop('phase_p3',self.phase_p3)

        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        elif hasattr(self,'Sw_channel') and chan == self.Sw_channel: # Sw channel is digital, just like PM mod channel
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        else:
            idx0 = np.where(tvals >= tvals[0] + self.risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.risetime)[0][-1] + 1

            start_p1 = np.where(tvals <= (tvals[0] + self.risetime))[0][-1]
            end_p1 = np.where(tvals <= (tvals[0] + self.length_p1 + self.risetime))[0][-1]
            start_p2 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay))[0][-1]
            end_p2 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2))[0][-1]
            start_p3 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2 + self.pulse_delay))[0][-1]
            end_p3 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2 + self.pulse_delay + \
                self.length_p3))[0][-1]

            wf = np.zeros(len(tvals))

            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

                print self.name, tvals[0]

            if chan == self.I_channel:
                wf[start_p1:end_p1] += self.env_p1_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_p1:end_p1] + self.phase_p1/360.))
                wf[start_p2:end_p2] -= self.env_p2_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_p2:end_p2] + self.phase_p2/360.))
                wf[start_p3:end_p3] += self.env_p3_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * tvals[start_p3:end_p3] + self.phase_p3/360.))

            if chan == self.Q_channel:
                wf[start_p1:end_p1] += self.env_p1_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_p1:end_p1] + self.phase_p1/360.))
                wf[start_p2:end_p2] -= self.env_p2_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_p2:end_p2] + self.phase_p2/360.))
                wf[start_p3:end_p3] += self.env_p3_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * tvals[start_p3:end_p3] + self.phase_p3/360.))

            return wf

class composite_pi2_pi_pi2_Hermite_pulse_IQ(MW_IQmod_pulse):
    def __init__(self, *arg, **kw):
        MW_IQmod_pulse.__init__(self, *arg,amplitude=1., **kw)

        self.length_p1 = kw.pop('length_p1', 0)
        self.length_p2 = kw.pop('length_p2', 0)
        self.length_p3 = kw.pop('length_p3', 0) 
        self.pulse_delay = kw.pop('pulse_delay', 1e-9)
        self.length = self.length_p1 + self.length_p2 + self.length_p3 + self.pulse_delay*2 +self.risetime*2

        self.env_p1_amplitude = kw.pop('amplitude_p1', 0.1)
        self.env_p2_amplitude = kw.pop('amplitude_p2', 0.1)
        self.env_p3_amplitude = kw.pop('amplitude_p3', 0.1)
        self.phase_p1 = kw.pop('phase_p1',0)
        self.phase_p2 = kw.pop('phase_p2',0)
        self.phase_p3 = kw.pop('phase_p3',0)

        self.mu_p1 = kw.pop('mu_p1',0.5*(self.length_p1+2*self.risetime))
        self.mu_p2 = kw.pop('mu_p2',0.5*(self.length_p2+2*self.pulse_delay+2*self.length_p1+2*self.risetime))
        self.mu_p3 = kw.pop('mu_p2',0.5*(self.length_p3+2*self.pulse_delay+2*self.length_p2+2*self.pulse_delay+2*self.length_p1+2*self.risetime))
        self.T_herm_p1 = kw.pop('T_herm_p1',0.1667*(self.length_p1)) 
        self.T_herm_p2 = kw.pop('T_herm_p2',0.1667*(self.length_p2)) 
        self.T_herm_p3 = kw.pop('T_herm_p3',0.1667*(self.length_p3)) 

        self.start_offset = self.risetime
        self.stop_offset = self.risetime

    def __call__(self, *arg, **kw):
        MW_IQmod_pulse.__call__(self, *arg,amplitude=1., **kw)

        self.length_p1 = kw.pop('length_p1', self.length_p1)
        self.length_p2 = kw.pop('length_p2', self.length_p2)
        self.length_p3 = kw.pop('length_p3', self.length_p3) 
        self.pulse_delay = kw.pop('pulse_delay', self.pulse_delay)
        self.length = self.length_p1 + self.length_p2 + self.length_p3 + self.pulse_delay*2 +self.risetime*2

        self.env_p1_amplitude = kw.pop('amplitude_p1', self.env_p1_amplitude)
        self.env_p2_amplitude = kw.pop('amplitude_p2', self.env_p2_amplitude)
        self.env_p3_amplitude = kw.pop('amplitude_p3', self.env_p3_amplitude)
        self.phase_p1 = kw.pop('phase_p1',self.phase_p1)
        self.phase_p2 = kw.pop('phase_p2',self.phase_p2)
        self.phase_p3 = kw.pop('phase_p3',self.phase_p3)

        self.mu_p1 = kw.pop('mu_p1',0.5*(self.length_p1+2*self.risetime))
        self.mu_p2 = kw.pop('mu_p2',0.5*(self.length_p2+2*self.pulse_delay+2*self.length_p1+2*self.risetime))
        self.mu_p3 = kw.pop('mu_p2',0.5*(self.length_p3+2*self.pulse_delay+2*self.length_p2+2*self.pulse_delay+2*self.length_p1+2*self.risetime))
        self.T_herm_p1 = kw.pop('T_herm_p1',0.1667*(self.length_p1)) 
        self.T_herm_p2 = kw.pop('T_herm_p2',0.1667*(self.length_p2)) 
        self.T_herm_p3 = kw.pop('T_herm_p3',0.1667*(self.length_p3)) 

        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        elif hasattr(self,'Sw_channel') and chan == self.Sw_channel: # Sw channel is digital, just like PM mod channel
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        else:
            idx0 = np.where(tvals >= tvals[0] + self.risetime)[0][0]
            idx1 = np.where(tvals <= tvals[0] + self.length - self.risetime)[0][-1] + 1

            start_p1 = np.where(tvals <= (tvals[0] + self.risetime))[0][-1]
            end_p1 = np.where(tvals <= (tvals[0] + self.length_p1 + self.risetime))[0][-1]
            start_p2 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay))[0][-1]
            end_p2 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2))[0][-1]
            start_p3 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2 + self.pulse_delay))[0][-1]
            end_p3 = np.where(tvals <= (tvals[0] + self.risetime + self.length_p1 + \
                self.pulse_delay + self.length_p2 + self.pulse_delay + \
                self.length_p3))[0][-1]

            wf = np.zeros(len(tvals))

            # in this case we start the wave with zero phase at the effective start time
            # (up to the specified phase)
            if not self.phaselock:
                tvals = tvals.copy() - tvals[idx0]

                print self.name, tvals[0]

            t_p1 = tvals[start_p1:end_p1]-tvals[0]
            t_p2 = tvals[start_p2:end_p2]-tvals[0]
            t_p3 = tvals[start_p3:end_p3]-tvals[0]

            if chan == self.I_channel:
                wf[start_p1:end_p1] += self.env_p1_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * t_p1 + self.phase_p1/360.))
                wf[start_p2:end_p2] -= self.env_p2_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * t_p2 + self.phase_p2/360.))
                wf[start_p3:end_p3] += self.env_p3_amplitude * np.cos(2 * np.pi * \
                    (self.frequency * t_p3 + self.phase_p3/360.))

            if chan == self.Q_channel:
                wf[start_p1:end_p1] += self.env_p1_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * t_p1 + self.phase_p1/360.))
                wf[start_p2:end_p2] -= self.env_p2_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * t_p2 + self.phase_p2/360.))
                wf[start_p3:end_p3] += self.env_p3_amplitude * np.sin(2 * np.pi * \
                    (self.frequency * t_p3 + self.phase_p3/360.))

            env = np.zeros(len(tvals))

            # print start_p1,end_p1,start_p2,end_p2,start_p3,end_p3
            # print self.mu_p1,self.mu_p2,self.mu_p3
            # print self.T_herm_p1,self.T_herm_p2,self.T_herm_p3

            (1-0.667*((t_p1-self.mu_p1)/self.T_herm_p1)**2)*np.exp(-((t_p1-self.mu_p1)/self.T_herm_p1)**2)

            env[start_p1:end_p1] = (1-0.667*((t_p1-self.mu_p1)/self.T_herm_p1)**2)*np.exp(-((t_p1-self.mu_p1)/self.T_herm_p1)**2) #literature value for pi2 pulse
            env[start_p2:end_p2] = (1-0.956*((t_p2-self.mu_p2)/self.T_herm_p2)**2)*np.exp(-((t_p2-self.mu_p2)/self.T_herm_p2)**2) #literature value for pi pulse
            env[start_p3:end_p3] = (1-0.667*((t_p3-self.mu_p3)/self.T_herm_p3)**2)*np.exp(-((t_p3-self.mu_p3)/self.T_herm_p3)**2) #literature value for pi2 pulse

            # print env[start_p1:end_p1]

            return wf*env


class MW_CORPSE_pulse(MW_pulse, CORPSE_pulse):

    # this is between the driving pulses (not PM)
    def __init__(self, *arg, **kw):
        MW_pulse.__init__(self, *arg, **kw)
        CORPSE_pulse.__init__(self, *arg, **kw)
           
    def __call__(self, **kw):
        MW_pulse.__call__(self, **kw)
        CORPSE_pulse.__call__(self, **kw)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return np.ones(len(tvals))

        else:
            start_1, end_1, start_2, end_2, start_3, end_3  = self._get_starts_ends(tvals)
            wf = np.zeros(len(tvals))
            
            wf[start_1:end_1] += self.amplitude 
            wf[start_2:end_2] -= self.amplitude 
            wf[start_3:end_3] += self.amplitude
            
            return wf 

class RF_erf_envelope(pulse.SinePulse):
    def __init__(self, *arg, **kw):
        pulse.SinePulse.__init__(self, *arg, **kw)

        self.envelope_risetime = kw.pop('envelope_risetime', 500e-9)

    def chan_wf(self, chan, tvals):
        wf = pulse.SinePulse.chan_wf(self, chan, tvals)
        
        # TODO make this nicer
        rt = self.envelope_risetime
        env = (ssp.erf(2./rt*(tvals-tvals[0]-rt))/2.+0.5) * \
                (ssp.erf(-2./rt*(tvals-tvals[-1]+rt))/2. + 0.5)

        return wf * env

# Written by MAB as the AWG rise element of an RF pulse with error function element
class RF_erf_rise_element(pulse.SinePulse):
    def __init__(self, *arg, **kw):
        pulse.SinePulse.__init__(self, *arg, **kw)

        self.envelope_risetime = kw.pop('envelope_risetime', 500e-9)
        self.startorend = kw.pop('startorend', None)

    def chan_wf(self, chan, tvals):
        wf = pulse.SinePulse.chan_wf(self, chan, tvals)
        
        rt = self.envelope_risetime
        if self.startorend == 'start':
            env = ssp.erf(2./rt*(tvals-tvals[0]-rt))/2.+0.5
        elif self.startorend == 'end':
            env = ssp.erf(-2./rt*(tvals-tvals[-1]+rt))/2. + 0.5
        else:
            raise Exception('RF pulse start or end incorrectly defined')
        return wf * env


class GaussianPulse_Envelope_IQ(MW_IQmod_pulse):
    def __init__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_IQmod_pulse.__init__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*self.length)
        self.std = kw.pop('std',0.1667*self.length)

    def __call__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', self.env_amplitude)
        MW_IQmod_pulse.__call__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*self.length)
        self.std = kw.pop('std',0.1667*self.length)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        else:  
            t=tvals-tvals[0] 
            env = self.env_amplitude*np.exp(-(((t-self.mu)**2)/(2*self.std**2)))
            wf = MW_IQmod_pulse.chan_wf(self, chan, tvals)

            return env*wf


class GaussianPulse_Envelope(MW_pulse):
    def __init__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_pulse.__init__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*self.length)
        self.std = kw.pop('std',0.1667*self.length)

    def __call__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', self.env_amplitude)
        MW_pulse.__call__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*self.length)
        self.std = kw.pop('std',0.1667*self.length)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_pulse.chan_wf(self,chan,tvals)

        else: 
            t=tvals-tvals[0]  
            env = self.env_amplitude*np.exp(-(((t-self.mu)**2)/(2*self.std**2)))
            wf = MW_pulse.chan_wf(self, chan, tvals)

            return env*wf


class HermitePulse_Envelope_IQ(MW_IQmod_pulse):
    def __init__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_IQmod_pulse.__init__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu', 0.5*self.length)
        self.T_herm = kw.pop('T_herm', 0.1667*(self.length - 2 * self.risetime)) # without MW switch: - 2 * self.PM_risetime
        self.pi2_pulse = kw.pop('pi2_pulse', False)


    def __call__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', self.env_amplitude)
        MW_IQmod_pulse.__call__(self, *arg,amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*self.length)
        self.T_herm = kw.pop('T_herm',0.1667*(self.length - 2 * self.risetime) ) # without MW switch: - 2 * self.PM_risetime (KvB, 028-05-2015)
        self.pi2_pulse = kw.pop('pi2_pulse', self.pi2_pulse)
 
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        elif hasattr(self,'Sw_channel') and chan == self.Sw_channel: # Sw channel is digital, just like PM mod channel
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        else: 
            t=tvals-tvals[0] 
            # env = self.env_amplitude*(1-0.956*((t-self.mu)/self.T_herm)**2)*np.exp(-((t-self.mu)/self.T_herm)**2)
            if self.pi2_pulse : # for  Hermite 90deg pulse
                env = self.env_amplitude*(1-0.667*((t-self.mu)/self.T_herm)**2)*np.exp(-((t-self.mu)/self.T_herm)**2) #literature values
            else : # for Hermite 180deg pulse
                env = self.env_amplitude*(1-0.956*((t-self.mu)/self.T_herm)**2)*np.exp(-((t-self.mu)/self.T_herm)**2) #literature values
            wf = MW_IQmod_pulse.chan_wf(self, chan, tvals)

            return env*wf

class HermitePulse_Envelope(MW_pulse):
    def __init__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_pulse.__init__(self, *arg,amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*(self.length))
        self.T_herm = kw.pop('T_herm',0.1667*(self.pulse_length))
        self.pi2_pulse = kw.pop('pi2_pulse', False)

    def __call__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', self.env_amplitude) 
        MW_pulse.__call__(self, *arg, amplitude=1., **kw)
        self.mu = kw.pop('mu',0.5*(self.length))
        self.T_herm = kw.pop('T_herm',0.1667*(self.pulse_length)) ## needed pulse_length for width calculation! AR & NK 20150522
        self.pi2_pulse = kw.pop('pi2_pulse', self.pi2_pulse)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_pulse.chan_wf(self,chan,tvals)

        else: 
            t=tvals-tvals[0]  #XXXXXXXXXXXXXXXXXXxx test pi/2 pulse !!
            
            if self.pi2_pulse : # for  Hermite 90deg pulse
                env = self.env_amplitude*(1-0.667*((t-self.mu)/self.T_herm)**2)*np.exp(-((t-self.mu)/self.T_herm)**2) #literature values
            else : # for Hermite 180deg pulse
                env = self.env_amplitude*(1-0.956*((t-self.mu)/self.T_herm)**2)*np.exp(-((t-self.mu)/self.T_herm)**2) #literature values
            wf = MW_pulse.chan_wf(self, chan, tvals)
            return env*wf



class ReburpPulse_Envelope_IQ(MW_IQmod_pulse):
    def __init__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_IQmod_pulse.__init__(self, *arg,amplitude=1., **kw)

    def __call__(self, *arg, **kw):
        self.env_amplitude = kw.pop('amplitude', 0.1)
        MW_IQmod_pulse.__call__(self, *arg,amplitude=1., **kw)
        return self

    def chan_wf(self, chan, tvals):
        if chan == self.PM_channel:
            return MW_IQmod_pulse.chan_wf(self,chan,tvals)

        else:  
            F_coeff = [0.49,-1.02,1.11,-1.57,0.83,-0.42,0.26,-0.16,+0.10,-0.07,+0.04,-0.03,+0.01,-0.02,0,0.01] \
        # Fourier series coefficients for Np = 256, taken from Geen and Freeman paper
            F_coeff[:] = [x*self.env_amplitude/6.114 for x in F_coeff] # /6.114 to get normalise max amplitude to 1

            Amp_Reburp_list=np.zeros((len(tvals),len(F_coeff)))
            Amp_Reburp = np.zeros((len(tvals)))
        
            for j in range(len(tvals)):
                for i,c in enumerate(F_coeff):  
                    Amp_Reburp_list[j,i] = c*np.cos(i*((2*np.pi)/self.length)*tvals[j])

                Amp_Reburp[j]= (sum(Amp_Reburp_list[j]))
            

            wf = MW_IQmod_pulse.chan_wf(self, chan, tvals)

            return Amp_Reburp*wf

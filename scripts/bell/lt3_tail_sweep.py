"""
LT3 script for Measuring a tail with a picoquant time correlator
"""


import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as bseq
reload(bseq)
import parameters as bparams
reload(bparams)


class EOMAOMPulse_step(pulse.Pulse):
    def __init__(self, name, eom_channel, aom_channel,  **kw):
        pulse.Pulse.__init__(self, name)
        self.eom_channel = eom_channel
        self.aom_channel = aom_channel

        self.channels = [eom_channel,aom_channel]
                                               
        self.eom_off_duration          = kw.pop('eom_off_duration'        ,100e-9)## we should try to make this shorter
        self.eom_off_amplitude         = kw.pop('eom_off_amplitude'       ,-.25)
        self.eom_off_2_amplitude       = kw.pop('eom_off_2_amplitude'     ,2.65)
        self.eom_overshoot_duration1   = kw.pop('eom_overshoot_duration1' ,10e-9)##check these
        self.eom_overshoot1            = kw.pop('eom_overshoot1'          ,0.03)##check these
        self.eom_overshoot_duration2   = kw.pop('eom_overshoot_duration2' ,4e-9)##check these
        self.eom_overshoot2            = kw.pop('eom_overshoot2'          ,0.03)##check these
        self.aom_risetime              = kw.pop('aom_risetime'            ,23e-9)
        self.aom_on                    = kw.pop('aom_on'                  ,True)

        self.start_offset   = self.eom_off_duration
        self.stop_offset    = 3*self.eom_off_duration
        self.length         = 4*self.eom_off_duration                                      
        
    def __call__(self,  **kw):
        self.eom_off_duration          = kw.pop('eom_off_duration'        ,self.eom_off_duration)
        self.eom_off_amplitude         = kw.pop('eom_off_amplitude'       ,self.eom_off_amplitude)
        self.eom_off_2_amplitude       = kw.pop('eom_off_2_amplitude'     ,self.eom_off_2_amplitude)
        self.eom_overshoot_duration1   = kw.pop('eom_overshoot_duration1' ,self.eom_overshoot_duration1)
        self.eom_overshoot1            = kw.pop('eom_overshoot1'          ,self.eom_overshoot1)
        self.eom_overshoot_duration2   = kw.pop('eom_overshoot_duration2' ,self.eom_overshoot_duration2)
        self.eom_overshoot2            = kw.pop('eom_overshoot2'          ,self.eom_overshoot2)
        self.aom_risetime              = kw.pop('aom_risetime'            ,self.aom_risetime)
        self.aom_on                    = kw.pop('aom_on'                  ,True)
        
        self.start_offset   = self.eom_off_duration
        self.stop_offset    = 3*self.eom_off_duration        
        self.length         = 4*self.eom_off_duration

        return self
        
    def chan_wf(self, channel, tvals):
        
        tvals -= tvals[0]
        tvals = np.round(tvals, pulsar.SIGNIFICANT_DIGITS) 
        
        if channel == self.eom_channel:

            off_time1_start     = 0
            off_time1_stop      = np.where(tvals <= self.eom_off_duration)[0][-1]
            
            overshoot1_stop     = np.where(tvals <= np.round(self.eom_off_duration + \
                                    self.eom_overshoot_duration1,
                                        pulsar.SIGNIFICANT_DIGITS))[0][-1]
            
            overshoot2_stop     = np.where(tvals <= np.round(self.eom_off_duration + \
                                    self.eom_overshoot_duration1 + \
                                    self.eom_overshoot_duration2,
                                        pulsar.SIGNIFICANT_DIGITS))[0][-1]
            
            off_time2_stop      = np.where(tvals <= np.round(self.eom_off_duration + \
                                     self.eom_off_duration,
                                        pulsar.SIGNIFICANT_DIGITS))[0][-1]
    
            #print len(tvals)
            pulse_wf = np.zeros(len(tvals)/2)
            pulse_wf[off_time1_start:off_time1_stop] += self.eom_off_amplitude
            pulse_wf[off_time1_stop:overshoot1_stop] += self.eom_overshoot1
            pulse_wf[overshoot1_stop:overshoot2_stop]+= self.eom_overshoot2
            pulse_wf[off_time1_stop:off_time2_stop]  += self.eom_off_2_amplitude

            #compensation_pulse
            comp_wf = np.zeros(len(tvals)/2)

            comp_amp = (self.eom_off_duration * self.eom_off_amplitude + \
                            self.eom_off_duration * self.eom_off_2_amplitude + \
                            self.eom_overshoot_duration1 * self.eom_overshoot1 + \
                            self.eom_overshoot_duration2 * self.eom_overshoot2) / (2 * self.eom_off_duration)

            comp_wf -= comp_amp

            wf = np.append(pulse_wf,comp_wf)


        if channel == self.aom_channel:

            wf = np.zeros(len(tvals))

            pulse_start = np.where(tvals <= np.round(self.eom_off_duration-self.aom_risetime, 
                pulsar.SIGNIFICANT_DIGITS))[0][-1]
            pulse_stop  = np.where(tvals <= np.round(self.eom_off_duration + self.aom_risetime, 
                                pulsar.SIGNIFICANT_DIGITS))[0][-1]

            wf[pulse_start:pulse_stop] += 1*self.aom_on 
            
        return wf

class EOMAOMPulse_raymond_step(pulse.Pulse):
    def __init__(self, name, eom_channel, aom_channel, eom_trigger_channel, **kw):
        pulse.Pulse.__init__(self, name)
        self.eom_channel = eom_channel
        self.aom_channel = aom_channel
        self.eom_trigger_channel = eom_trigger_channel

        self.channels = [eom_channel,aom_channel,eom_trigger_channel]
                                               
        self.eom_pulse_duration        = kw.pop('eom_pulse_duration'      ,80e-9)
        self.eom_pulse_amplitude       = kw.pop('eom_pulse_amplitude'     ,3.0) 
        self.eom_comp_pulse_amplitude  = kw.pop('eom_comp_pulse_amplitude',0.25*self.eom_pulse_amplitude)

        self.eom_trigger_amplitude     = kw.pop('eom_trigger_amplitude'   ,1.0)
        self.aom_risetime              = kw.pop('aom_risetime'            ,23e-9)
        self.aom_amplitude             = kw.pop('aom_amplitude'           ,1.0)

        self.start_offset   = self.eom_pulse_duration
        self.stop_offset    = 4*self.eom_pulse_duration
        self.length         = 5*self.eom_pulse_duration
        
    def __call__(self,  **kw):
        return self
        
       
    def chan_wf(self, channel, tvals):

        tvals -= tvals[0]
        tvals = np.round(tvals, pulsar.SIGNIFICANT_DIGITS) 

        if channel == self.eom_trigger_channel:

            trigger_pulse_start = np.where(tvals <= self.eom_pulse_duration)[0][-1]
            trigger_pulse_stop = np.where(tvals <= 2.*self.eom_pulse_duration)[0][-1]

            wf = np.zeros(len(tvals))
            wf[trigger_pulse_start:trigger_pulse_stop] += self.eom_trigger_amplitude

        elif channel == self.eom_channel:

            opt_pulse1_start     = np.where(tvals <= np.round(0.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            opt_pulse1_stop      = np.where(tvals <= np.round(1.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            opt_pulse2_start     = np.where(tvals <= np.round(2.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            opt_pulse2_stop      = np.where(tvals <= np.round(4.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
  
            #print len(tvals)
            wf = np.zeros(len(tvals))
            wf[opt_pulse1_start:opt_pulse1_stop] += self.eom_pulse_amplitude
            wf[opt_pulse2_start:opt_pulse2_stop] -= self.eom_comp_pulse_amplitude

        elif channel == self.aom_channel:

            wf = np.zeros(len(tvals))
            pulse_start     = np.where(tvals <= np.round(self.eom_pulse_duration-self.aom_risetime, \
                    pulsar.SIGNIFICANT_DIGITS))[0][-1]
            pulse_stop      = np.where(tvals <= np.round(self.eom_pulse_duration+self.aom_risetime, \
                    pulsar.SIGNIFICANT_DIGITS))[0][-1]

            wf[pulse_start:pulse_stop] += self.aom_amplitude
            
        return wf

class EOMAOMPulse_raymond_pulse(pulse.Pulse):
    def __init__(self, name, eom_channel, aom_channel, eom_trigger_channel, **kw):
        pulse.Pulse.__init__(self, name)
        self.eom_channel = eom_channel
        self.aom_channel = aom_channel
        self.eom_trigger_channel = eom_trigger_channel

        self.channels = [eom_channel,aom_channel,eom_trigger_channel]
                                               
        self.eom_pulse_duration        = kw.pop('eom_pulse_duration'      ,50e-9)
        self.eom_pulse_amplitude       = kw.pop('eom_pulse_amplitude'     ,1.45) 

        self.eom_trigger_duration      = kw.pop('eom_trigger_eom_trigger_duration'  ,60e-9)
        self.eom_trigger_amplitude     = kw.pop('eom_trigger_amplitude'             ,1.0)
        self.eom_trigger_pulse_duration= kw.pop('eom_trigger_pulse_duration'        ,1e-9)
        self.aom_risetime              = kw.pop('aom_risetime'                      ,23e-9)
        self.aom_amplitude             = kw.pop('aom_amplitude'                     ,1.0)
        
        self.eom_comp_pulse_amplitude  = kw.pop('eom_comp_pulse_amplitude',\
                self.eom_pulse_amplitude*self.eom_trigger_pulse_duration/self.eom_pulse_duration)

        self.start_offset   = self.eom_trigger_duration
        self.stop_offset    = 3*self.eom_trigger_duration
        self.length         = 4*self.eom_trigger_duration + 2*self.eom_trigger_pulse_duration
        
    def __call__(self,  **kw):
        return self
        
       
    def chan_wf(self, channel, tvals):

        tvals -= tvals[0]
        tvals = np.round(tvals, pulsar.SIGNIFICANT_DIGITS) 
        
        if channel == self.eom_trigger_channel:

            trigger1_pulse_start = 0
            trigger1_pulse_stop  = np.where(tvals <= np.round(self.eom_trigger_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            print len(tvals), trigger1_pulse_stop
            trigger2_pulse_start = np.where(tvals <= np.round(self.eom_trigger_duration + self.eom_trigger_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            
            wf = np.zeros(len(tvals)/2)
            wf[trigger1_pulse_start:trigger1_pulse_stop] += self.eom_trigger_amplitude
            wf[trigger2_pulse_start:] += self.eom_trigger_amplitude

            wf=np.append(wf,np.zeros(len(tvals)/2))

        elif channel == self.eom_channel:

            opt_pulse_start     = np.where(tvals <= np.round(self.eom_trigger_duration+\
                    0.5*self.eom_trigger_pulse_duration-0.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
            opt_pulse_stop      = np.where(tvals <= np.round(self.eom_trigger_duration+\
                    0.5*self.eom_trigger_pulse_duration+0.5*self.eom_pulse_duration,pulsar.SIGNIFICANT_DIGITS))[0][-1]
  
            #print len(tvals)
            wf = np.zeros(len(tvals)/2)
            wf[opt_pulse_start:opt_pulse_stop] += self.eom_pulse_amplitude

             #compensation_pulse
            comp_wf = np.zeros(len(tvals)/2)
            comp_wf[opt_pulse_start:opt_pulse_stop] -= self.eom_comp_pulse_amplitude

            wf = np.append(wf,comp_wf)

        elif channel == self.aom_channel:

            wf = np.zeros(len(tvals))
            pulse_start     = np.where(tvals <= np.round(self.eom_trigger_duration-self.aom_risetime, \
                    pulsar.SIGNIFICANT_DIGITS))[0][-1]
            pulse_stop      = np.where(tvals <= np.round(self.eom_trigger_duration+self.eom_trigger_pulse_duration\
                    +self.aom_risetime,pulsar.SIGNIFICANT_DIGITS))[0][-1]

            wf[pulse_start:pulse_stop] += self.aom_amplitude
            
        return wf

class LT3Tail(pulsar_pq.PQPulsarMeasurement):

    def generate_sequence(self):
        print 'generating'
        self.lt3_sequence()

    
    def autoconfig(self, **kw):
        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)

        # add values from AWG calibrations
        self.params_lt3['SP_voltage_AWG'] = \
                self.A_aom_lt3.power_to_voltage(
                        self.params_lt3['AWG_SP_power'], controller='sec')

        print 'setting AWG SP voltage:', self.params_lt3['SP_voltage_AWG']
        
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params_lt3['SP_voltage_AWG'])


    def lt3_sequence(self):
        print "Make lt3 sequence... "
               
        self.lt3_seq = pulsar.Sequence('TailLT3')

        elements = [] 

        dummy_element = bseq._lt3_dummy_element(self)
        finished_element = bseq._lt3_sequence_finished_element(self)
        elements.append(dummy_element)
        elements.append(finished_element)

        for i in range(self.params['pts']):
            eom_p = self.create_eom_pulse(i)
            e = bseq._lt3_LDE_element(self, 
                name = 'LT3 Tail sweep element {}'.format(i),
               eom_pulse =  eom_p)    
            elements.append(e)
            self.lt3_seq.append(name = 'LT3 Tail sweep {}'.format(i),
                wfname = e.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.params['LDE_attempts_before_CR'])
            
        qt.pulsar.upload(*elements)
        qt.pulsar.program_sequence(self.lt3_seq)

    def create_eom_pulse(self, i):
        if self.params['use_eom_pulse'] == 'short':
            print 'using short eom pulse'
            return EOMAOMPulse_step('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_off_duration = self.params['eom_off_duration'],
                    eom_off_amplitude = self.params['eom_off_amplitude'],
                    eom_off_2_amplitude  = 2.65, #msmt.params_lt3['eom_off_2_amplitude'],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'],
                    eom_overshoot1 = 0.0, #msmt.params_lt3['eom_overshoot1'],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2 = 0.0, #msmt.params_lt3['eom_overshoot2'],
                    aom_risetime = self.params['aom_risetime']) 
        elif self.params['use_eom_pulse'] == 'raymond-pulse':
            return EOMAOMPulse_raymond_pulse('Eom Aom Pulse', 
                    eom_channel             = 'EOM_Matisse',
                    aom_channel             = 'EOM_AOM_Matisse',
                    eom_trigger_channel     = 'EOM_trigger',
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_comp_pulse_amplitude= self.params['eom_comp_pulse_amplitude'][i],
                    eom_trigger_duration      = self.params['eom_trigger_duration'],
                    eom_trigger_pulse_duration= self.params['eom_trigger_pulse_duration'],
                    eom_trigger_amplitude   = self.params['eom_trigger_amplitude'],
                    aom_risetime            = self.params['aom_risetime'],
                    aom_amplitude           = self.params['aom_amplitude'][i])
        elif self.params['use_eom_pulse'] == 'raymond-step':
            return EOMAOMPulse_raymond_step('Eom Aom Pulse', 
                    eom_channel             = 'EOM_Matisse',
                    aom_channel             = 'EOM_AOM_Matisse',
                    eom_trigger_channel     = 'EOM_trigger',
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_comp_pulse_amplitude= self.params['eom_comp_pulse_amplitude'][i],
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_trigger_amplitude   = self.params['eom_trigger_amplitude'],
                    aom_risetime            = self.params['aom_risetime'],
                    aom_amplitude           = self.params['aom_amplitude'][i])
        else: 
            return pulselib.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_pulse_duration      = self.params['eom_pulse_duration'][i],
                    eom_off_duration        = self.params['eom_off_duration'],
                    eom_off_amplitude       = self.params['eom_off_amplitude'][i],
                    eom_pulse_amplitude     = self.params['eom_pulse_amplitude'][i],
                    eom_overshoot_duration1 = self.params['eom_overshoot_duration1'],
                    eom_overshoot1          = self.params['eom_overshoot1'][i],
                    eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                    eom_overshoot2          = self.params['eom_overshoot2'],
                    aom_risetime            = self.params['aom_risetime'],
                    aom_amplitude           = self.params['aom_amplitude'][i])


LT3Tail.adwin_dict = adwins_cfg.config
LT3Tail.green_aom_lt3 = qt.instruments['GreenAOM']
LT3Tail.Ey_aom_lt3 = qt.instruments['MatisseAOM']
LT3Tail.A_aom_lt3 = qt.instruments['NewfocusAOM']
LT3Tail.mwsrc_lt3 = qt.instruments['SMB100']
LT3Tail.awg_lt3 = qt.instruments['AWG']
LT3Tail.repump_aom_lt3 = qt.instruments['GreenAOM']

def tail_lt3(name):

    m=LT3Tail(name)
    
    for k in bparams.params.parameters:
        m.params[k] = bparams.params[k]
    for k in bparams.params_lt3.parameters:
        m.params[k] = bparams.params_lt3[k]

    m.params_lt3=m.params
    SAMPLE_CFG = qt.exp_params['protocols']['current']
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params['Ex_CR_amplitude']= m.params['Ey_CR_amplitude']
    m.params['Ex_SP_amplitude']= m.params['Ey_SP_amplitude']
    m.params['Ex_RO_amplitude']=m.params['Ey_RO_amplitude']

    pts=1
    m.params['pts']=pts
    
    #EOM pulse ----------------------------------
    #qt.pulsar.set_channel_opt('EOM_trigger', 'delay', 147e-9)
    #qt.pulsar.set_channel_opt('EOM_trigger', 'high', 2.)#2.0

    m.params['use_eom_pulse'] = 'raymond-step' #'short', 'raymond-pulse', 'raymond-step'
    m.params['eom_off_amplitude']         = np.ones(pts)*-0.07#np.linspace(-0.1,0.05,pts) # calibration from 19-03-2014
    m.params['aom_risetime']              = 25e-9#42e-9 # calibration to be done!
   
    if m.params['use_eom_pulse'] == 'raymond-pulse':

        m.params['eom_pulse_amplitude']         = np.ones(pts)*1.45 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']          = np.ones(pts)* 60e-9
        m.params['eom_trigger_duration']        = 80e-9
        m.params['eom_trigger_pulse_duration']  = 1e-9
        m.params['eom_trigger_amplitude']       = 1.0
        m.params['eom_comp_pulse_amplitude']    = (m.params['eom_trigger_duration']*m.params['eom_off_amplitude'] \
                                                    +m.params['eom_trigger_pulse_duration']*m.params['eom_pulse_amplitude'] )/m.params['eom_pulse_duration']  
    elif m.params['use_eom_pulse'] == 'raymond-step': 

        m.params['eom_pulse_amplitude']        = np.ones(pts)*2.9 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']         = np.ones(pts)* 100e-9
        m.params['eom_trigger_amplitude']      = 1.0
        m.params['eom_comp_pulse_amplitude']   = (0.5*m.params['eom_pulse_duration']*m.params['eom_pulse_amplitude'] \
                                                    +m.params['eom_pulse_duration']*m.params['eom_off_amplitude'] )/(2.*m.params['eom_pulse_duration'])  
    else:#'normal':

        m.params['eom_pulse_amplitude']        = np.ones(pts)*1.5 #(for long pulses it is 1.45, dor short:2.0)calibration from 19-03-2014# 
        m.params['eom_pulse_duration']         = np.ones(pts)* 2e-9
        m.params['eom_comp_pulse_amplitude']   = m.params['eom_pulse_amplitude'] 
        m.params['eom_off_duration']           = 200e-9
        m.params['eom_overshoot_duration1']    = 10e-9
        m.params['eom_overshoot1']             = np.ones(pts)*-0.03 # calibration from 19-03-2014# 
        m.params['eom_overshoot_duration2']    = 10e-9
        m.params['eom_overshoot2']             = 0
        m.params['eom_aom_on']                = True
    
    p_aom= qt.instruments['PulseAOM']
    max_power_aom=p_aom.voltage_to_power(p_aom.get_V_max())
    aom_power_sweep=linspace(0.1,1.0,pts)*max_power_aom #%power
    aom_voltage_sweep = np.zeros(pts)
    for i,p in enumerate(aom_power_sweep):
        aom_voltage_sweep[i]= p_aom.power_to_voltage(p)

    m.params['aom_amplitude']             = np.ones(pts)*1.0#aom_voltage_sweep#np.ones(pts)*1.0#aom_voltage_sweep 

    m.params['sweep_name'] = 'aom_amplitude [percent]'
    m.params['sweep_pts'] = aom_power_sweep/max_power_aom


    bseq.pulse_defs_lt3(m)

    m.params['send_AWG_start'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['syncs_per_sweep'] = m.params['LDE_attempts_before_CR']
    m.params['repetitions'] = 10000
    m.params['sequence_wait_time'] = m.params['LDE_attempts_before_CR']*m.params['LDE_element_length']*1e6 + 20
    m.params['SP_duration'] = 250

    m.params['opt_pi_pulses'] = 1
    m.params_lt3['MW_during_LDE'] = 0
    debug=True
    m.params['trigger_wait'] = not(debug)

    m.autoconfig()
    m.generate_sequence()
    
    if not debug:
        m.setup(mw=m.params_lt3['MW_during_LDE'], pq_calibrate=False)
        m.run(autoconfig=False, setup=False)    
        m.save()
        m.finish()


if __name__ == '__main__':
    tail_lt3('lt3_tailS_SIL5_Ex+8deg')
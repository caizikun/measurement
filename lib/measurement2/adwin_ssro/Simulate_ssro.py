"""
Class for SSRO with the Adwin
Cast into Simulate 20171130 @CEB for m1_sim_setup
"""
import numpy as np
import logging

import qt

import measurement.lib.measurement2.Simulate_measurement as m2


class AdwinSSRO(m2.AdwinControlledMeasurement):

    mprefix = 'AdwinSSRO'
    max_repetitions = 20000
    max_SP_bins = 500
    max_SSRO_dim = 1000000
    adwin_process = 'singleshot'
    E_aom = None
    A_aom = None
    repump_aom = None
    adwin = None
    
        
    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """
        # print self.E_aom.get.name()
        # self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
        #         [self.E_aom.get_pri_channel()]
        # self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
        #         [self.A_aom.get_pri_channel()]
        # self.params['repump_laser_DAC_channel'] = self.adwin.get_dac_channels()\
        #         [self.repump_aom.get_pri_channel()]    

        # if self.params['cr_mod']:
        #     self.params['repump_mod_DAC_channel'] = self.adwin.get_dac_channels()[self.params['repump_mod_control_dac']]
        #     self.params['repump_mod_control_offset'] = self.adwin.get_dac_voltage(self.params['repump_mod_control_dac'])
        #     self.params['cr_mod_DAC_channel']     = self.adwin.get_dac_channels()[self.params['cr_mod_control_dac']]#ssro.AdwinSSRO.adwin.get_dac_channels()['gate']

        # self.params['Ex_CR_voltage'] = self.E_aom.power_to_voltage(self.params['Ex_CR_amplitude'])
        # self.params['A_CR_voltage'] = self.A_aom.power_to_voltage(self.params['A_CR_amplitude'])
        # self.params['Ex_SP_voltage'] = self.E_aom.power_to_voltage(self.params['Ex_SP_amplitude'])
        # self.params['A_SP_voltage'] = self.A_aom.power_to_voltage(self.params['A_SP_amplitude'])
        # self.params['Ex_RO_voltage'] = self.E_aom.power_to_voltage(self.params['Ex_RO_amplitude'])
        # self.params['A_RO_voltage'] = self.A_aom.power_to_voltage(self.params['A_RO_amplitude'])
        # self.params['repump_voltage'] = self.repump_aom.power_to_voltage(self.params['repump_amplitude'])
        # self.params['repump_off_voltage'] = self.repump_aom.get_pri_V_off()
        # self.params['A_off_voltage'] = self.A_aom.get_pri_V_off()
        # self.params['Ex_off_voltage'] = self.E_aom.get_pri_V_off()

        m2.AdwinControlledMeasurement.autoconfig(self)

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """
        
        self.repump_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        self.repump_aom.set_cur_controller('ADWIN')
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.repump_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)        
    
    def set_adwin_process_variable_from_params(self,key):
        try:
            # Here we can do some checks on the settings in the adwin
            if np.isnan(self.params[key]):
                raise Exception('Adwin process variable {} contains NAN'.format(key))
            self.adwin_process_params[key] = self.params[key]
        except:
            logging.error("Cannot set adwin process variable '%s'" \
                    % key)
            raise Exception('Adwin process variable {} has not been set in the measurement params dictionary!'.format(key))

    def run(self, autoconfig=True, setup=True):
        
        if autoconfig:
            self.autoconfig()         
        if setup:
            self.setup()
        print 'SSRO'
        print self.adwin_process
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        aborted=False
        CR_counts = 0
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                aborted = True
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('completed_reps')
            #print self.adwin_var('total_CR_counts')
            CR_counts = self.adwin_var('total_CR_counts') - CR_counts
            
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['SSRO_repetitions']))
            # print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()
        # qt.msleep(1)
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))
        return not(aborted)

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps * self.params['SSRO_duration']),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])

    def finish(self, **kw):

        self.repump_aom.set_power(0)
        self.E_aom.set_power(0)
        self.A_aom.set_power(0)

        m2.AdwinControlledMeasurement.finish(self, **kw)

class AdwinSSROAlternCR(AdwinSSRO):   
    adwin_process = 'singleshot_altern_CR'
    mprefix = 'AdwinSSROAlternCR'
    
    def __init__(self, name):
        AdwinSSRO.__init__(self, name)
        
        
class IntegratedSSRO(AdwinSSRO):
    adwin_process = 'integrated_ssro'
    mprefix = 'IntegratedSSRO'

    # remote_helper = None

    def __init__(self, name):
        AdwinSSRO.__init__(self, name)
        
    def autoconfig(self):
        ### These parameters are defined before AdwinSSRO.autoconfig, since they are used there.
        self.params['SSRO_repetitions'] = \
            self.params['pts'] * self.params['repetitions']
        self.params['sweep_length'] = self.params['pts']
        
        AdwinSSRO.autoconfig(self)
        
        ### broadcast msmt_params to QT Monitor for live plotting
        ### needs a working instance of a remote_msmt_helper & qtlab monitor otherwise error!
        # self.remote_helper.set_measurement_params(self.params)

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', self.params['pts']),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])
        

        

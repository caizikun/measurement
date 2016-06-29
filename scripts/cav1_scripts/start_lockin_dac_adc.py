import qt
import measurement.lib.measurement2.measurement as m2
reload(m2)
import measurement.lib.config.adwins as adwins_cfg
reload(adwins_cfg)

class Lockin_Dac_Adc(m2.AdwinControlledMeasurement):

    adwin_process = 'lockin_dac_adc'
    adwin_dict = adwins_cfg.config
    adwin_processes_key = 'adwin_cav1_processes'
    
    def autoconfig(self):
        for key,_val in self.adwin_dict[self.adwin_processes_key][self.adwin_process]['params_long']:              
            self.set_adwin_process_variable_from_params(key)

        for key,_val in self.adwin_dict[self.adwin_processes_key][self.adwin_process]['params_float']:              
            self.set_adwin_process_variable_from_params(key)

    def run(self):
        self.start_adwin_process(stop_processes=['counter'])

    def stop(self):
        self.stop_adwin_process()
        self.finish()

    def finish(self, save_params=True, save_stack=False, 
            stack_depth=4, save_ins_settings=True):
      
        if save_params:
            self.save_params()
            
        if save_stack:
            self.save_stack(depth=stack_depth)
           
        if save_ins_settings:
            self.save_instrument_settings_file()

        m2.AdwinControlledMeasurement.finish(self)

if __name__ == '__main__':
    m=Lockin_Dac_Adc('test1')
    m.adwin = qt.instruments['adwin']
    
    
    m.params['output_dac_channel'] = m.adwin.get_dac_channels()['newfocus_freqmod']
    m.params['input_adc_channel']  = 16 
    m.params['modulation_bins']    = 200 #number of
    m.params['error_averaging'] = 50
    m.params['modulation_amplitude'] = 0.15 #V
    m.params['modulation_frequency'] = 600 #Hz
    print 'aprox. read_interval:', 1./m.params['modulation_frequency'] * m.params['error_averaging']

    m.autoconfig()
    m.run()

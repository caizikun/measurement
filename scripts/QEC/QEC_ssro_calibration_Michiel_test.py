"""
script for adwin ssro calibration.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']


def run(self, autoconfig=True, setup=True):
    if autoconfig:
        self.autoconfig()
        
    if setup:
        self.setup()
    print self.adwin_process
    self.start_adwin_process(stop_processes=['counter'])
    qt.msleep(1)
    self.start_keystroke_monitor('abort',timer=False)
    
    CR_counts = 0
    while self.adwin_process_running():
        self._keystroke_check('abort')
        if self.keystroke('abort') in ['q','Q']:
            print 'aborted.'
            self.stop_keystroke_monitor('abort')
            break
        
        reps_completed = self.adwin_var('completed_reps')
        #print self.adwin_var('total_CR_counts')
        CR_counts = self.adwin_var('total_CR_counts') - CR_counts
        print CR_counts
        
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

def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    
    if RO_power != None: 
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None: 
        m.params['SSRO_duration'] = SSRO_duration

    m.params['CR_preselect'] = 10000
    m.params['CR_probe'] = 10000
    m.params['CR_repump'] = 10000

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    run(m)
    m.save('ms0')
    
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
    #ssrocalibration(SAMPLE_CFG, RO_power = 0.5e-9,SSRO_duration = 100)

    # RO_powers = [0.2e-9,0.5e-9,1e-9,2e-9,5e-9]
    # for RO_power in RO_powers: 
    #     print 'RO_power = %s W' %RO_power 
    #     ssrocalibration(SAMPLE_CFG,RO_power = RO_power,SSRO_duration = 50)
    #     ri = raw_input ('Do Fitting. Press c to continue. \n')
    #     if str(ri) != 'c':
    #         break
    #  NOTE: If you want to measure make sure you analyse a normal ssro as last 
    # TODO: Make a simple SSRO analysis script that does not edit the config. 

import qt
import numpy as np
import time
import logging
import purify_slave
from collections import deque
import measurement.lib.measurement2.measurement as m2
import purify_slave, LDE_storage_sweep
import measurement.lib.measurement2.pq.pq_measurement as pq; reload(pq)
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import copy
import msvcrt
reload(pq)
reload(purify_slave);reload(LDE_storage_sweep)

name = qt.exp_params['protocols']['current']

class PQPurifyMeasurement(purify_slave.purify_single_setup,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'PQ_C13_Measurement'
    adwin_process = 'purification'
    
    def __init__(self, name):
        purify_slave.purify_single_setup.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def autoconfig(self):
        purify_slave.purify_single_setup.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        purify_slave.purify_single_setup.setup(self,**kw)
        pq.PQMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        self.start_adwin_process(load=False)
        qt.msleep(.5)

    def measurement_process_running(self):
        return self.adwin_process_running()

    def run(self, **kw):
        pq.PQMeasurement.run(self,**kw)
        
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def stop_measurement_process(self):
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))


class purify(PQPurifyMeasurement):
    mprefix = 'Purification'
    adwin_process = 'purification'

    def __init__(self, name):
        PQPurifyMeasurement.__init__(self, name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1
    
    def save(self, name = 'adwindata'):
        purify_slave.purify_single_setup.save(self)     

    
    def finish(self):
        h5_joint_params_group = self.h5basegroup.create_group('joint_params')
        joint_params = self.joint_params.to_dict()
        for k in joint_params:
            h5_joint_params_group.attrs[k] = joint_params[k]
        self.h5data.flush()

        self.AWG_RO_AOM.turn_off()
        self.E_aom.turn_off()
        self.A_aom.turn_off()
        self.repump_aom.turn_off()


        PQPurifyMeasurement.finish(self)

    def stop_measurement_process(self):
        PQPurifyMeasurement.stop_measurement_process(self)


def MW_Position(name,debug = False,upload_only=False):
    """
    Put a very long repumper. Leave one MW pi pulse to find the microwave position.
    NK 2017
    """

    m = purify(name)
    LDE_storage_sweep.prepare(m)


    LDE_storage_sweep.turn_all_sequence_elements_off(m)
    
        ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 10000


    ### sequence specific parameters
    m.params['sync_during_LDE'] = 1
    m.params['do_LDE_1'] = 1
    m.params['MW_during_LDE'] = 1
    m.params['skip_LDE_mw_pi'] = 1
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE1_attempts'] = 1
    
    m.params['first_mw_pulse_type'] = 'square'
    m.params['LDE_SP_duration'] = 10e-6
    m.params['Square_pi_amp'] = 0.02
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'Square_pi_length'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.array([1e-6])#np.linspace(0.5e-6,2e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9
    m.params['is_two_setup_experiment']= 0  
    # m.params['AWG_SP_power'] = 100e-9
    ### upload and run

    LDE_storage_sweep.run_sweep(m,debug = debug,upload_only = upload_only)


if __name__ == '__main__':

    ########### local measurements
    MW_Position(name+'_MW_position',upload_only=False)
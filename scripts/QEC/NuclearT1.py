"""
Script for carbonT1 msmnts
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearT1(name,tau = None, 
                    carbon_state = 'up', 
                    electron_RO = 'positive', 
                    carbon = 1,
                    el_RO_result = 0,
                    el_after_init=0,
                    pts=11,
                    short_time=1.0e-3,
                    long_time=20.0e-3):

    m = DD.NuclearT1(name)
    funcs.prepare(m)

    '''set experimental parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 500 #Repetitions of each data point
    m.params['pts'] = pts

    m.params['Addressed_Carbon']             = carbon
    m.params['C13_init_state']               = carbon_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state'] = el_RO_result
    m.params['el_after_init'] = el_after_init #if ==1 then a micrwave pi pulse prings the electorn into ms=-1


    m.params['sweep_name'] = 'wait_times'
    m.params['wait_times'] = np.linspace(short_time,long_time,m.params['pts']) #Note: wait time must be at least carbon init time +5us 
    m.params['sweep_pts']  = m.params['wait_times']

    m.params['Nr_C13_init']         = 1

    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0


    #############################
    #!NB: These should go into msmt params
    #############################

    ##########
    # Overwrite certain params to test their influence on the sequence.
    m.params['C13_MBI_threshold_list']      = [0]
    m.params['C13_MBI_RO_duration']         = 100
    m.params['SP_duration_after_C13']       = 250
        
    # m.autoconfig() (autoconfig is firs line in funcs.finish )
    funcs.finish(m, upload =True, debug=True)

if __name__ == '__main__':


    
    ## Carbon up and down
    NuclearT1(SAMPLE + 'up_positive_C5_elState0',carbon_state = 'up', 
            electron_RO = 'positive', carbon = 5,
            el_RO_result = 0,
            el_after_init=0)

    # NuclearT1(SAMPLE + 'up_positive_C1_elState1',carbon_state = 'up', 
    #         electron_RO = 'positive', carbon = 1,
    #         el_RO_result = 0,
    #         el_after_init=0)

    #######
    # List of consecutive measurements, planned for the night of 20141105
    #######
    
    # C13_list = [5,2]
    # eRo_List = ['positive','negative']
    # el_init_list = [0,1]
    # timing_points_list = [[0.0005,0.05,11],[0.05,0.5,11],[0.5,1.3,7]]


    # for C in C13_list:
    #     for t_list in timing_points_list:
    #         for eRo in eRo_List:
    #             for el_init in el_init_list:
    #                 GreenAOM.set_power(10e-6)
    #                 optimiz0r.optimize(dims=['x','y','z','x','y'])
    #                 msmt_string = eRo + '_C'+ str(C) + '_el_state' +  str(el_init) + 'longestTime' + str(t_list[1])
    #                 NuclearT1(SAMPLE + 'up_'+ msmt_string,carbon_state = 'up', 
    #                     electron_RO = eRo, carbon = C,
    #                     el_RO_result = 0,
    #                     el_after_init=el_init,
    #                     pts=t_list[2],
    #                     short_time=t_list[0],
    #                     long_time=t_list[1])

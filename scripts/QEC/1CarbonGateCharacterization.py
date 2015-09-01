import numpy as np
import qt 
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Single_C_gate_characterization(name, 
        carbon_nr             = 1,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        el_during_experiment  = 1, 
        C13_init_method       = 'MBI',
        C13_MBI_threshold     = [1],
        C13_RO_basis          = ['Y'],
        nr_of_gates_list      = np.linspace(0,5,6),
        gate_phase            = 'Y',
        constant_time         = False,
        reps                  = 200):

    m = DD.Nuclear_gate_characterization(name)
    funcs.prepare(m)

    '''Set parameters'''

    m.params['el_during_experiment'] = el_during_experiment # 1 or 0 or 'sup'
    if m.params['el_during_experiment'] == 1:
        m.params['el_after_init'] ='1'
    else:
        m.params['el_after_init'] ='0'

    m.params['nr_of_gates_list'] = nr_of_gates_list

    m.params['pts'] = len(nr_of_gates_list)
    ### Derive other parameters

    m.params['sweep_name']          = 'Nr of gates' 
    m.params['sweep_pts']           = nr_of_gates_list

    m.params['constant_time'] = constant_time

    m.params['gate_phase'] = 'C13_'+gate_phase+'_phase'


    ### Sweep parameters
    m.params['reps_per_ROsequence'] = reps

    m.params['C13_MBI_RO_state'] = 0 
    m.params['C13_MBI_threshold_list'] = C13_MBI_threshold

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['C_RO_basis']                   = C13_RO_basis

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    m.params['use_shutter'] = 0

    funcs.finish(m, upload =True, debug=False)

def qstop(sleep):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':
    n = 1
    # c = 1
    # Single_C_gate_characterization(SAMPLE+'positive_constant_time_prt1_carbon_'+str(c), 
    #                 el_RO= 'positive',carbon_nr = c,nr_of_gates_list= np.linspace(0,4,2))

    for c in [5]:
        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            n = 0


        el_during_list = [0,1]
        for el_during in el_during_list:

            for C13_RO_basis in ['X','Z']:
                print '--------------------------------'
                print 'press q to stop measurement loop'
                print '--------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    n = 0

                if n ==1:
                    Single_C_gate_characterization(SAMPLE+'positive_prt1_carbon_'+str(c)+'_RO_'+C13_RO_basis+'_'+str(el_during), el_during_experiment  = el_during, C13_RO_basis = [C13_RO_basis], el_RO= 'positive',carbon_nr = c,nr_of_gates_list= np.linspace(0,8,5))
                    Single_C_gate_characterization(SAMPLE+'negative_prt1_carbon_'+str(c)+'_RO_'+C13_RO_basis+'_'+str(el_during), el_during_experiment  = el_during, C13_RO_basis = [C13_RO_basis], el_RO= 'negative',carbon_nr = c,nr_of_gates_list= np.linspace(0,8,5))
                
                print '--------------------------------'
                print 'press q to stop measurement loop'
                print '--------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    n = 0
                
                if n ==1:
                    Single_C_gate_characterization(SAMPLE+'positive_prt2_carbon_'+str(c)+'_RO_'+C13_RO_basis+'_'+str(el_during), el_during_experiment  = el_during, C13_RO_basis = [C13_RO_basis], el_RO= 'positive',carbon_nr = c,nr_of_gates_list= np.linspace(10,14,2))
                    Single_C_gate_characterization(SAMPLE+'negative_prt2_carbon_'+str(c)+'_RO_'+C13_RO_basis+'_'+str(el_during), el_during_experiment  = el_during, C13_RO_basis = [C13_RO_basis], el_RO= 'negative',carbon_nr = c,nr_of_gates_list= np.linspace(10,14,2))
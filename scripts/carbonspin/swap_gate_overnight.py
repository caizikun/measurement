''' overnight swapperino '''
''' step 1. do 1_carbon_Initialization
    step 2. do swap_carbon gate
    both are literally copied into here, cause I dont know how to run two scripts in sequence -.- '''


#########################################
''' 1_carbon_Initialization Benchmark!'''
#########################################
import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
from measurement.scripts.carbonspin.1_carbon_Initialization import MBE
from measurement.scripts.carbonspin.swap_gate_sten import SWAP




SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']




if __name__ == '__main__':

    print 'Starting Loop, engage!'

    carbons = [1, 2, 3, 5, 6]
    debug = False
    init_method = 'both'

    if init_method == 'both' or init_method == 'swap':
        for c in carbons:

            breakst = stools.show_stopper()
            if breakst:
                break

            MBE(SAMPLE + 'positive_'+str(c)+'_swap', el_RO= 'positive', carbon = c, carbon_init_list = [c]
                                                ,debug = debug,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])


            MBE(SAMPLE + 'negative_'+str(c)+'_swap', el_RO= 'negative', carbon = c, carbon_init_list = [c]
                                                ,debug = debug,carbon_init_methods     =   ['swap'], carbon_init_thresholds  =   [0])
            
            if init_method == 'both':
                init_method = 'MBI'

    if init_method == 'MBI':
        for c in carbons:


            breakst = stools.show_stopper()
            if breakst:
                break
            MBE(SAMPLE + 'positive_'+str(c)+'_MBI', el_RO= 'positive', carbon = c, carbon_init_list = [c]
                                                ,carbon_init_methods     =   ['MBI'], carbon_init_thresholds  =   [1])

            MBE(SAMPLE + 'negative_'+str(c)+'_MBI', el_RO= 'negative', carbon = c, carbon_init_list = [c]
                                                ,carbon_init_methods     =   ['MBI'], carbon_init_thresholds  =   [1])



    init_method = 'swap'
    el_state    = ['X','-X','Y','-Y','Z','-Z']
    RO_after_swap = [True, False]

    for r in RO_after_swap:

        if RO_after_swap == True:
            c_i_t = [0, 1]
        else:
            c_i_t = [0]


        for e in el_state:
            print 'Loop over electron state!'

            breakst = stools.show_stopper() or breakst
            if breakst:
                break

            for c in carbons:
                breakst = stools.show_stopper() or breakst
                if breakst:
                    break

                print 'Loop over carbons number!'

                SWAP(SAMPLE + '_carbon' + str(c) + '_elState'+str(e)+'_swapRO_'+str(r)+'_positive', 
                    el_RO= 'positive', carbon = c
                    ,debug = debug, elec_init_state = e, RO_after_swap = RO_after_swap,
                    carbon_init_thresholds = c_i_t)


                SWAP(SAMPLE + '_carbon' + str(c) + '_elState'+str(e)+'_swapRO_'+str(r)+'_negative', 
                    el_RO= 'negative', carbon = c
                     ,debug = debug, elec_init_state = e, RO_after_swap = RO_after_swap,
                     carbon_init_thresholds = c_i_t)
else: 
    print 'Fail'

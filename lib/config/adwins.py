config = {}
config['adwin_lt1_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 8,  # dac 3 is no longer working with the ATTO CONTROLLER!
        'yellow_aom_frq': 4,
        'newfocus_frq' : 5, #not yet N
        'velocity1_aom' : 6,
        'velocity2_aom' : 7,
        'yellow_aom' : 3, #IT WORKS FINE FOR THE AOM CONTROLLER THOUGH.
        }

config['adwin_lt1_dios'] = {
        'awg_event' : 6,
        'awg_trigger' : 0,
        'awg_ch3m2' : 9,
        'lt1_zpl_wp' : 4,
        }

config['adwin_lt1_processes'] = {

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },


        'linescan' : {

            'index' : 2,
            'file' : 'lt1_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {

            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'lt1_simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'resonant_counting' : {

             'doc' : '',
             'index' : 1,
             'file' : 'lt1_resonant_counting.TB1',
             'par' : {
                 'set_aom_dac' : 63,
                 'set_aom_duration' : 73,
                 'set_probe_duration' : 74,
                 },
             'fpar' : {
                 'set_aom_voltage' : 64,
                 'floating_average': 11, #floating average time (ms)
                 },
             'data_float' : {
                 'get_counts' : [41,42,43,44],
                 },
             },

        'set_dac' :  {
            'index' : 3,
            'file' : 'lt1_set_dac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'lt1_set_ttl_outputs.TB4',
            'par' : {
                'dio_no' : 61,
                'dio_val' : 62,
                },
            },

        'trigger_dio' : {
            'index' : 4,
            'file' : 'lt1_dio_trigger.tb4',
            'par' : {
                'dio_no' : 61,
                'startval' : 62, # where to start - 0 or 1
                'waittime' : 63, # length of the trigger pulse in units of 10 ns
            },
        },

        # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr.inc',
            'par' : {
                    'CR_preselect'   : 75,
                    'CR_probe'       : 68,
                    'CR_repump'      : 69,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'  : 76,
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },
# ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
# For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
# Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'SSRO.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },
                },

        # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check_mod_pos' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_mod.inc',
            'par' : {
                    'CR_preselect'              : 75,
                    'CR_probe'                  : 68,
                    'CR_repump'                 : 69,
                    'total_CR_counts'           : 70,
                    'noof_repumps'              : 71,
                    'noof_cr_checks'            : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'             : 76,
                    'pos_mod_activate'          : 65,
                    'repump_mod_activate'       : 66,
                    'cr_mod_activate'           : 67,
                    'cur_pos_mod_dac'           : 64,
                    },
                    'fpar' : {
                    'repump_mod_err' : 78,
                    'cr_mod_err'     : 79,
                    'pos_mod_err'    : 64,

                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ['repump_mod_DAC_channel'      ,   7],
                    ['cr_mod_DAC_channel'          ,   8],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'           ,   0.8],
                    ['repump_off_voltage'       ,  0.07],
                    ['Ex_CR_voltage'            ,   0.8],
                    ['A_CR_voltage'             ,   0.8],
                    ['Ex_off_voltage'           ,   0.0],
                    ['A_off_voltage'            , -0.08],
                    ['repump_mod_control_offset',   0.0],
                    ['repump_mod_control_amp'   ,   0.0],
                    ['cr_mod_control_offset'    ,   0.0],
                    ['cr_mod_control_amp'       ,   0.0],
                    ['pos_mod_control_amp'      ,  0.03],
                    ['pos_mod_fb'               ,   0.1],
                    ['pos_mod_min_counts'       ,  300.]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                'data_float' : {
                    'atto_positions' : 16
                    }
                },
# ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check_mod' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_mod.inc',
            'par' : {
                    'CR_preselect'              : 75,
                    'CR_probe'                  : 68,
                    'CR_repump'                 : 69,
                    'total_CR_counts'           : 70,
                    'noof_repumps'              : 71,
                    'noof_cr_checks'            : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'             : 76,
                    'repump_mod_activate'       : 66,
                    'cr_mod_activate'           : 67,
                    },
                    'fpar' : {
                    'repump_mod_err' : 78,
                    'cr_mod_err'     : 79,

                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ['repump_mod_DAC_channel'      ,   7],
                    ['cr_mod_DAC_channel'          ,   8],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'           ,   0.8],
                    ['repump_off_voltage'       ,  0.07],
                    ['Ex_CR_voltage'            ,   0.8],
                    ['A_CR_voltage'             ,   0.8],
                    ['Ex_off_voltage'           ,   0.0],
                    ['A_off_voltage'            , -0.08],
                    ['repump_mod_control_offset',   0.0],
                    ['repump_mod_control_amp'   ,   0.0],
                    ['cr_mod_control_offset'    ,   0.0],
                    ['cr_mod_control_amp'       ,   0.0],
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt1.tb9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt1.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'green_readout' : {
            'index' : 9,
            'file'  : 'green_readout_lt1.TB9',
            'params_long' : [
                ['AWG_start_DO_channel'         ,   16],
                ['AWG_event_jump_DO_channel'    ,   8 ],
                ['total_sync_nr'                ,   5], 
                ['sync_counter_idx'                  ,   4],
            ],
            'params_long_index' : 20,
            'params_long_length': 10,
            'par'               : {
                'completed_reps'    : 73,
            },
        },

        'integrated_ssro_msp1' : {
                'index' : 9,
                'file' : 'integrated_ssro_msp1_lt1.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'RO_msp1_data' : 27,
                    },
                },


        'adaptive_magnetometry' : {
                'index' : 9,
                'file' : 'adaptive_magnetometry_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['do_adaptive'                 ,   0],
                    ['adptv_steps'                 ,   5],
                    ['ch1'                         ,   0],
                    ['ch2'                         ,   0],
                    ['ch3'                         ,   0],
                    ['ch4'                         ,   0],
                    ['ch5'                         ,   0],
                    ['ch6'                         ,   0],
                    ['ch7'                         ,   0],
                    ['ch8'                         ,   0],
                    ['do_phase_calibr'             ,   1],
                    ['M'                           ,   1], #number of measurements per adaptive step
                    ['threshold_majority_vote'     ,   0],
                    ['reps_majority_vote'          ,   1],
                    ['AWG_event_jump_DO_channel'   ,   0],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 32,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'set_phase' : 24,
                    'RO_data' : 25,
                    'phases':27,
                    }
                },


        'adaptive_magnetometry_realtime' : {
                'index' : 9,
                'file' : 'adaptive_magnetometry_superoptimized_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['wait_for_AWG_done'           ,   0],
                    ['AWG_event_jump_DO_channel'   ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['do_adaptive'                 ,   0],
                    ['adptv_steps'                 ,   5],
                    ['ch1'                         ,   0],
                    ['ch2'                         ,   0],
                    ['ch3'                         ,   0],
                    ['ch4'                         ,   0],
                    ['ch5'                         ,   0],
                    ['ch6'                         ,   0],
                    ['ch7'                         ,   0],
                    ['ch8'                         ,   0],
                    ['do_ext_test'                 ,   1],
                    ['M'                           ,   1], #number of measurements per adaptive step
                    ['threshold_majority_vote'     ,   0],
                    ['reps_majority_vote'          ,   1],
                    ['G'                           ,   0],
                    ['F'                           ,   0],
                    ['save_pk_n'                   ,   0],
                    ['save_pk_m'                   ,   0],   
                    ['do_add_phase'                ,   0],                 
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 32,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['fid0'                        ,   1],
                    ['fid1'                        ,   1],
                    ['T2'                          ,   1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'set_phase' : 24,
                    'RO_data' : 25,
                    'phases':27,
                    'ext_msmnt_results': 28,
                    'timer': 29,
                    },
                'data_float' : {
                    'theta' :33,
                    #'real_p_k': 38,
                    #'imag_p_k':39
                    }
                },


        'adaptive_magnetometry_realtime_swarm' : {
                'index' : 9,
                'file' : 'adaptive_magnetometry_superoptimized_berry_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['wait_for_AWG_done'           ,   0],
                    ['AWG_event_jump_DO_channel'   ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['do_adaptive'                 ,   0],
                    ['adptv_steps'                 ,   5],
                    ['ch1'                         ,   0],
                    ['ch2'                         ,   0],
                    ['ch3'                         ,   0],
                    ['ch4'                         ,   0],
                    ['ch5'                         ,   0],
                    ['ch6'                         ,   0],
                    ['ch7'                         ,   0],
                    ['ch8'                         ,   0],
                    ['do_ext_test'                 ,   1],
                    ['M'                           ,   1], #number of measurements per adaptive step
                    ['threshold_majority_vote'     ,   0],
                    ['reps_majority_vote'          ,   1],
                    ['G'                           ,   0],
                    ['F'                           ,   0],
                    ['save_pk_n'                   ,   0],
                    ['save_pk_m'                   ,   0],   
                    ['do_add_phase'                ,   0],                 
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 32,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['fid0'                        ,   1],
                    ['fid1'                        ,   1],
                    ['T2'                          ,   1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'set_phase' : 24,
                    'RO_data' : 25,
                    'phases':27,
                    'ext_msmnt_results': 28,
                    'timer': 29,
                    },
                'data_float' : {
                    'theta' :33,
                    'swarm_u0': 50,
                    'swarm_u1': 51,
                    }
                },



        'adaptive_magnetometry_realtime_debug' : {
                'index' : 9,
                'file' : 'adaptive_magnetometry_realtime_variableM_DEBUG_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['wait_for_AWG_done'           ,   0],
                    ['AWG_event_jump_DO_channel'   ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['do_adaptive'                 ,   0],
                    ['adptv_steps'                 ,   5],
                    ['ch1'                         ,   0],
                    ['ch2'                         ,   0],
                    ['ch3'                         ,   0],
                    ['ch4'                         ,   0],
                    ['ch5'                         ,   0],
                    ['ch6'                         ,   0],
                    ['ch7'                         ,   0],
                    ['ch8'                         ,   0],
                    ['do_ext_test'                 ,   1],
                    ['M'                           ,   1], #number of measurements per adaptive step
                    ['threshold_majority_vote'     ,   0],
                    ['reps_majority_vote'          ,   1],
                    ['G'                           ,   0],
                    ['F'                           ,   0],
                    ['save_pk_n'                   ,   0],
                    ['save_pk_m'                   ,   0],                    
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 32,
                'params_float' : [
                    ['fid0'                        ,   1],
                    ['fid1'                        ,   1],
                    ['T2'                          ,   1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'set_phase' : 24,
                    'RO_data' : 25,
                    'phases':27,
                    'ext_msmnt_results': 28,
                    'timer': 29,
                    'debug1':40,
                    'debug2':41,
                    'debug3':42,
                    'debug4':43,
                    },
                'data_float' : {
                    'theta' :33,
                    'real_p_tn' :34,
                    'real_p_2tn' :35,
                    'imag_p_tn' :36,
                    'imag_p_2tn' :37,
                    'real_p_k' : 38,
                    'imag_p_k' :39,
                    }
                },






        'bell' : {
                'index' : 9,
                'file' : 'bell_lt1.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_done_DI_channel'         ,   8],
                    ['AWG_success_DI_channel'         ,   8],
                    ['SP_duration'                 , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['remote_CR_DO_channel'        ,  15],
                    ['SSRO_duration'               ,  50],
                    ['wait_for_AWG_done'           ,   1],
                    ['sequence_wait_time'          ,  10],
                    ['wait_before_RO'              ,  10],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'        , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'        , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'local_mode': 61,
                    'timeout_events': 62,
                    'stop_flag': 63,
                    'completed_reps' : 73,
                    'entanglement_events': 77,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'CR_timer': 27,
                    'CR_hist':  28,
                    },
                },
                # one CR check followed by multiple times SP-AWG seg-SSRO-repump-delaytime
        'ssro_multiple_RO' : {
                'index' : 9,
                'file' : 'integrated_ssro_multiple_RO_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['SP_repump_duration'          ,   1],
                    ['wait_time_between_msmnts'    ,   1],
		            ['repump_E'    		           ,   0],
		            ['repump_A'    		           ,   0],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'process_time' : 80,
                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt1.TB9',
                'include_cr_process' : 'cr_check_mod',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'MBI start': 78,
                    'ROseq_cntr': 80,

                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'teleportation' : {

                'info' : """
                    Teleportation master control. LT1 is local, LT2 is remote.
                    """,
                'index' : 9,
                'file' : 'lt1_teleportation_control.TB9',
                'params_long' : [           #Keep order!!!
                    ['counter_channel'              ,       1],
                    ['repump_laser_DAC_channel'     ,       3],
                    ['E_laser_DAC_channel'          ,       6],
                    ['A_laser_DAC_channel'          ,       7],
                    ['CR_duration'                  ,      50],
                    ['CR_threshold_preselect'       ,      30],
                    ['CR_threshold_probe'           ,      10],
                    ['repump_duration'              ,     100],
                    ['E_SP_duration'                ,      50],
                    ['SSRO_duration'                ,      20],
                    ['ADwin_lt2_trigger_do_channel' ,       2],
                    ['ADWin_lt2_di_channel'         ,       1],
                    ['AWG_lt1_trigger_do_channel'   ,       1],
                    ['AWG_lt1_di_channel'           ,       3],
                    ['PLU_arm_do_channel'           ,      10],
                    ['PLU_di_channel'               ,       2],
                    ['MBI_duration'                 ,       4],
                    ['CR_repump'                    ,    1000],
                    ['AWG_lt1_event_do_channel'     ,       3],
                    ['AWG_lt2_RO1_bit_channel'      ,       1],
                    ['AWG_lt2_RO2_bit_channel'      ,       0],
                    ['AWG_lt2_do_DD_bit_channel'    ,       2],
                    ['AWG_lt2_strobe_channel'       ,       9],
                    ['A_SP_duration'                ,       5],
                    ['do_sequences'                 ,       1],
                    ['CR_probe_max_time'            , 1000000],
                    ['MBI_threshold'                ,       1],
                    ['max_MBI_attempts'             ,       1],
                    ['N_randomize_duration'         ,      50],
                    ['wait_before_send_BSM_done'    ,      30],
                    ],
                'params_long_index'    : 20,
                'params_long_length'   : 40,
                'params_float' : [
                    ['repump_voltage'               ,   0.0],
                    ['repump_off_voltage'           ,     0],
                    ['E_CR_voltage'                 ,   0.0],
                    ['A_CR_voltage'                 ,   0.0],
                    ['E_SP_voltage'                 ,   0.0],
                    ['A_SP_voltage'                 ,   0.0],
                    ['E_RO_voltage'                 ,   0.0],
                    ['A_RO_voltage'                 ,   0.0],
                    ['E_off_voltage'                ,   0.0],
                    ['A_off_voltage'                ,   0.0],
                    ['E_N_randomize_voltage',           0.0],
                    ['A_N_randomize_voltage',           0.0],
                    ['repump_N_randomize_voltage',      0.0],
                    ],
                'params_float_index'    : 21,
                'params_float_length'   : 10,
                'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'completed_reps' : 77,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76,
                    'noof_starts' : 78,
                    'kill_by_CR' : 50,
                    },
                'data_long' : {
                    'CR_hist_time_out' : 7,
                    'CR_hist_all' : 8,
                    'repump_hist_time_out' : 9,
                    'repump_hist_all' : 10,
                    'CR_after' : 23,
                    'statistics' : 28,
                    'SSRO1_results' : 24,
                    'SSRO2_results' : 26,
                    # 'PLU_Bell_states' : 25, we took that out for now (oct 7, 2013)
                    'CR_before' : 27,
                    'CR_probe_timer': 29,
                    'CR_probe_timer_all': 30,
                    'CR_timer_lt2': 31,
                    },
                },
            ###########################
        ### QEC Carbon Control ####
        ###########################

        'MBI_single_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and one Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_single_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    ['C13_MBI_threshold'           ,   1],
                    ['C13_MBI_RO_duration'            ,  10],
                    ['SP_duration_after_C13'       ,  25],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['E_SP_voltage_after_C13_MBI'   , 0.0],
                    ['A_SP_voltage_after_C13_MBI'   , 0.0],
                    ['E_C13_MBI_RO_voltage'            , 0.0],


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'MBI_multiple_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and one Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_multiple_lt1.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],  #1
                    ['AWG_done_DI_channel'         ,   9],  #2
                    ['SP_E_duration'               , 100],  #3
                    ['wait_after_pulse_duration'   ,   1],  #4
                    ['repetitions'                 ,1000],  #5
                    ['sweep_length'                ,  10],  #6
                    ['cycle_duration'              , 300],  #7 #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],  #8
                    ['MBI_duration'                ,   1],  #9
                    ['max_MBI_attempts'            ,   1],  #10
                    ['nr_of_ROsequences'           ,   1],  #11
                    ['wait_after_RO_pulse_duration',   3],  #12
                    ['N_randomize_duration'        ,  50],  #13

                    ['Nr_C13_init'                 ,  2],   #14
                    ['Nr_MBE'                      ,  1],   #15
                    ['Nr_parity_msmts'             ,  0],   #16
                      #Thresholds
                    ['MBI_threshold'               ,  1],   #17
                    # ['C13_MBI_threshold'           ,  0],   #18
                    ['MBE_threshold'               ,  1],   #19
                    ['Parity_threshold'            ,  1],   #20
                    # Durations
                    ['C13_MBI_RO_duration'         , 30],   #21
                    ['SP_duration_after_C13'       , 25],   #22

                    ['MBE_RO_duration'             ,  10],  #23
                    ['SP_duration_after_MBE'       ,  25],  #24

                    ['Parity_RO_duration'          ,  100],  #25
                    ['C13_MBI_RO_state'              ,  0 ],  #26
                    #Shutter
                    ['use_shutter'                 ,   0], #26 (the real 26 as 17 is commented out)
                    ['Shutter_channel'             ,   4], #27
                    ['Shutter_rise_time'           ,    3000], #28   
                    ['Shutter_fall_time'           ,    3000], #29
                    ['Shutter_safety_time'           ,  200000], #30
                    #['wait_between_runs'           , 0], #31
                    ],

                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8], #1
                    ['Ex_MBI_voltage'               , 0.8], #2
                    ['Ex_N_randomize_voltage'       , 0.0], #3
                    ['A_N_randomize_voltage'        , 0.0], #4
                    ['repump_N_randomize_voltage'   , 0.0], #5
                    ['E_C13_MBI_RO_voltage'         , 0.0], #6
                    ['E_SP_voltage_after_C13_MBI'   , 0.0], #7
                    ['A_SP_voltage_after_C13_MBI'   , 0.0], #8

                    ['E_MBE_RO_voltage'           , 1e-9], #9
                    ['A_SP_voltage_after_MBE'     , 15e-9],#10
                    ['E_SP_voltage_after_MBE'     , 0e-9], #11

                    ['E_Parity_RO_voltage'        , 1e-9], #12


                    # TODO_MAR: Add voltages for MBE and Parity


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'N_MBI_attempts' : 24,  #attempts since CR check, in success run
                    'N_MBI_starts' : 25,
                    'N_MBI_success' : 28,
                    'ssro_results' : 27,
                    'C13_MBI_starts' : 29,
                    'C13_MBI_success' : 32,
                    'C13_MBE_starts' : 51,
                    'C13_MBE_success': 52,
                    'parity_RO_results': 53,
                    },
                },            
        }

config['adwin_lt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'yellow_aom_frq' : 4,
        'yellow_aom' : 5,
        'matisse_aom' : 6,
        'green_aom': 7,
        'newfocus_aom' : 8,
        }

config['adwin_lt2_dios'] = {

        }

config['adwin_lt2_processes'] = {

        'linescan' : {

            'index' : 2,
            'file' : 'lt2_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                'set_phase_locking_on' : 19,
                'set_gate_good_phase' : 18,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'resonant_counting' : {
            'doc' : '',
            'index' : 1,
            'file' : 'resonant_counting.TB1',
            'par' : {
                'set_aom_dac' : 26,
                'set_aom_duration' : 27,
                'set_probe_duration' : 28,
                'set_gate_dac': 12,
                },
            'fpar' : {
                'set_aom_voltage' : 30,
                'floating_average': 11, #floating average time (ms)
                'gate_voltage' : 12,
                },
            'data_float' : {
                'get_counts' : [41,42,43,44],
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'SetDac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'Set_TTL_Outputs_LTsetup2.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },

       # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_pro.inc',
            'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76,
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },
# ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
# For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
# Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'ssro_pro.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt2.tb9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['Shutter_channel'             ,   4],
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

                # ADwin single-shot readout with yellow freq aom scan

        # ADwin conditional segmented SSRO
        'segmented_ssro' : {
                'index' : 9,
                'file' : 'ssro_segmented_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,  1],
                    ['CR_repump'                   ,  0],
                    ['segmented_RO_duration'        , 20],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['repump_voltage' , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08],
                    ['segmented_Ex_RO_voltage',0.1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
				'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    #'RO_data' : 25,
                    'statistics' : 26,
                    'segment_number' : 27,
                    'full_RO_data' : 28,
                    'segmented_RO_data' : 29,
                    },
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['wait_after_RO_pulse_duration',1],
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },
        'T1_without_AWG_SHUTTER' : {
                'index' : 9,
                'file' : 'T1_without_AWG_SHUTTER_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   16], #1
                    ['AWG_done_DI_channel'         ,    8], #2
                    ['send_AWG_start'              ,    0], #3
                    ['wait_for_AWG_done'           ,    0], #4
                    ['SP_duration'                 ,  100], #5
                    ['SP_filter_duration'          ,    0], #6
                    ['sequence_wait_time'          ,    0], #7
                    ['wait_after_pulse_duration'   ,    1], #8
                    ['SSRO_repetitions'            , 1000], #9
                    ['SSRO_duration'               ,   50], #10
                    ['SSRO_stop_after_first_photon',    0], #11
                    ['cycle_duration'              ,  300], #12  #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,    1], #13
                    ['use_shutter'                 ,    0], #14
                    ['Shutter_channel'             ,    4], #15
                    ['Shutter_opening_time'        , 3000], #16
                    ['Shutter_safety_time'         ,200000], #17
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'T1_wait_times' : 28,
                    },
                },
                # one CR check followed by multiple times SP-AWG seg-SSRO-repump-delay
        'ssro_multiple_RO' : {
                'index' : 9,
                'file' : 'integrated_ssro_multiple_RO_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['SP_repump_duration'          ,   1],
                    ['wait_time_between_msmnts'    ,   1],
		    ['repump_E'    		   ,   0],
		    ['repump_A'    		   ,   0],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['A_SP_repump_voltage'  ,0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],

                    #Shutter
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4], 
                    ['Shutter_rise_time'           ,    3000],    
                    ['Shutter_fall_time'           ,    3000], 
                    ['Shutter_safety_time'          ,  200000],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['A_SP_voltage_before_MBI'      , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'MBI_shutter' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    Has shutter included
                    """,
                'index' : 9,
                'file' : 'MBI__shutter_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    #Shutter
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4], 
                    ['Shutter_rise_time'           ,    3000],    
                    ['Shutter_fall_time'           ,    3000], 
                    ['Shutter_safety_time'           ,  200000],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['A_SP_voltage_before_MBI'      , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'adaptive_magnetometry' : {
                'index' : 9,
                'file' : 'adaptive_magnetometry_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['do_adaptive'                 ,   0],
                    ['adptv_steps'                 ,   5],
                    ['ch1'                         ,   0],
                    ['ch2'                         ,   0],
                    ['ch3'                         ,   0],
                    ['ch4'                         ,   0],
                    ['ch5'                         ,   0],
                    ['ch6'                         ,   0],
                    ['ch7'                         ,   0],
                    ['ch8'                         ,   0],
                    ['do_phase_calibr'             ,   1],
                    ['M'                           ,   1], #number of measurements per adaptive step
                    ['threshold_majority_vote'     ,   0],
                    
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],

                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'set_phase' : 24,
                    'RO_data' : 25,
                    'phases':27,
                    },
                },

        'general_pulses_sweep' : {
                'index' : 9,
                'file' : 'general_pulses_sweep.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   4],
                    ['dac1_channel'                ,   7],
                    ['dac2_channel'                ,   6],
                    ['dac3_channel'                ,   8],
                    ['max_element'                 ,   4],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['wait_after_pulse_duration'   ,   1],
                    ['max_sweep'                   ,  10],
                    ['sweep_channel'               ,   7],
                    ['do_sweep_duration'           ,   0],
                    ['sweep_element'               ,  10],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 11,
                'par' : {
                    'repetition_counter'      : 73,
                    'total_counts'            : 15,
                    },
                'data_float': {
                    'dac1_voltages'             : 21,
                    'dac2_voltages'             : 22,
                    'dac3_voltages'             : 23,
                    'sweep_voltages'            : 26,
                    },
                'data_long': {
                    'counter_on'                : 24,
                    'element_durations'         : 25,
                    'results'                   : 30,
                    'histogram'                 : 31,
                    'counter'                   : 32,
                    'sweep_durations'           : 27,
                    },
                },

        'general_pulses_repeat' : {
                'index' : 9,
                'file' : 'general_pulses_repeat.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   4],
                    ['dac1_channel'                ,   7],
                    ['dac2_channel'                ,   6],
                    ['dac3_channel'                ,   8],
                    ['max_element'                 ,   4],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['wait_after_pulse_duration'   ,   1],
                    ['max_repetitions'             ,10000],
                    ['timed_element'               ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 11,
                'par' : {
                    'repetition_counter'      : 72,
                    'total_counts'            : 70,
                    },
                'data_float': {
                    'dac1_voltages'             : 21,
                    'dac2_voltages'             : 22,
                    'dac3_voltages'             : 23,
                    },
                'data_long': {
                    'counter_on'                : 24,
                    'element_durations'         : 25,
                    'results'                   : 30,
                    'histogram'                 : 31,
                    'first_count'               : 32,
                    },
                },

        'MBI_Multiple_RO' : {  #with conditional repump, resonant, MBI
                'index' : 9,
                'file' : 'MBI_Multiple_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   1],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_E_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['CR_probe'                    ,  10],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['wait_for_MBI_pulse'          ,   4],
                    ['SP_A_duration'               , 300],
                    ['MBI_threshold'               , 0  ],
                    ['nr_of_RO_steps'              ,1],
                    ['do_incr_RO_steps'            ,0 ],
                    ['incr_RO_steps'               ,1],
                    ['wait_after_RO_pulse_duration',3 ],
                    ['final_RO_duration'           ,50]
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.0],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_final_RO_voltage'  , 0.8],
                    ['A_final_RO_voltage'   , 0]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'set_phase_locking_on'      : 19,
                    'set_gate_good_phase'       : 18,}
                },

        'MBI_feedback' : {  #with conditional repump, resonant, MBI,and addaptive feedback
                'index' : 9,
                'file' : 'MBI_Feedback_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['green_laser_DAC_channel'     ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,   1],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['green_repump_duration'       ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_E_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['RO_repetitions'              ,1000],
                    ['RO_duration'                 ,  50],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['CR_probe'                    ,  10],
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['wait_for_MBI_pulse'          ,   4],
                    ['SP_A_duration'               , 300],
                    ['MBI_threshold'               , 0  ],
                    ['wait_after_RO_pulse_duration',3   ],
                    ['final_RO_duration'           , 48 ],
                    ['wait_before_final_SP'        , 1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 30,
                'params_float' : [
                    ['green_repump_voltage' , 0.8],
                    ['green_off_voltage'    , 0.0],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_final_RO_voltage'  , 0.8],
                    ['A_final_RO_voltage'   , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 15,
                'par' : {
                    'set_phase_locking_on'      : 19,
                    'set_gate_good_phase'       : 18,},

                'data_long' : {
                    'CR_before'                 : 22,
                    'SP'                        : 24,
                    'CR_after_SSRO'             : 23,
                    'PLU_state'                 : 24,
                    'statistics'                : 26,
                    'SN'                        : 30,
                    'FS'                        : 31,
                    'FF'                        : 32,
                    'FinalRO_SN'                : 35,
                    'FinalRO_FS'                : 36,
                    'FinalRO_FF'                : 37,
                    },
                },
        #MBI + segmented RO (Can in the future be included with other adwin program - Machiel)

        'MBI_segmented_ssro' : {
                'index' : 9,
                'file' : 'ssro_MBI_segmented_RO_lt2.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['CR_preselect'                ,  10],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['CR_probe'                    ,  10],
                    ['repump_after_repetitions'    ,  1],
                    ['CR_repump'                   ,  0],
                    ['AWG_event_jump_DO_channel'    ,6],
                    ['segmented_RO_duration'        , 20],
                    ['MBI_duration'                 ,9],
                    ['wait_for_MBI_pulse'           ,3],
                    ['MBI_threshold'                ,1 ],
                    ['sweep_length'                 ,1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 30,
                'params_float' : [
                    ['repump_voltage' , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08],
                    ['segmented_Ex_RO_voltage',0.1]
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    'total_CR_counts' : 70,
                    'CR_threshold' : 25,
                    'last_CR_counts' : 26,
                    },
				'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'SP_hist' : 24,
                    #'RO_data' : 25,
                    'statistics' : 26,
                    'segment_number' : 27,
                    'full_RO_data' : 28,
                    'segmented_RO_data' : 29,
                    },
                },

        'teleportation' : {
                'index' : 9,
                'file' : 'lt2_teleportation.TB9',
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ey_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,  50],
                    ['CR_duration'                 ,  50],
                    ['CR_preselect'                ,  40],
                    ['teleportation_repetitions'   ,1000],
                    ['SSRO_lt2_duration'           ,  50],
                    ['CR_probe'                    ,  40],
                    ['CR_repump'                   ,1000],
                    ['Adwin_lt1_do_channel'        ,   8],
                    ['Adwin_lt1_di_channel'        ,  17],
                    ['AWG_lt2_di_channel'          ,  16],
                    ['freq_AOM_DAC_channel'        ,  4],
                    ['CR_probe_max_time'        , 1000000],
                    ],
                'params_long_index' : 20,
                'params_long_length': 25,
                'params_float' : [
                    ['repump_voltage'              , 0.0],
                    ['repump_off_voltage'          , 0.0],
                    ['Ey_CR_voltage'               , 0.0],
                    ['A_CR_voltage'                , 0.0],
                    ['Ey_SP_voltage'               , 0.0],
                    ['A_SP_voltage'                , 0.0],
                    ['Ey_RO_voltage'               , 0.0],
                    ['A_RO_voltage'                , 0.0],
                    ['Ey_off_voltage'              , 0.0],
                    ['A_off_voltage'               , 0.0],
                    ['repump_freq_offset'          , 5.0],
                    ['repump_freq_amplitude'       , 4.0]
                    ],
                'params_float_index' : 21,
                'params_float_length': 12,
                'par': {
                    'completed_reps' : 77,
                    'total_CR_counts': 70,
                    'get_noof_cr_checks' : 72,
                    'get_cr_below_threshold_events': 71,
                    'repump_counts': 76,
                    'noof_repumps': 66,
                    'kill_by_CR' : 50,
                    },
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after'  : 23,
                    'CR_hist'   : 24,
                    'repump_hist_time_out' : 9,
                    'repump_hist_all' : 10,
                    'SSRO_lt2_data' : 25,
                    'statistics'    : 26,
                    'CR_probe_timer' : 28,
                    'CR_hist_time_out' : 29,
                    },
                'data_float': {
                    'repump_freq_voltages'      : 19,
                    'repump_freq_counts'        : 27,
                    },
                },

        #gate modulation
        'check_trigger_from_lt1' : {
                'index' : 9,
                'file' : 'check_trigger_from_lt1.TB9',
                'par' : {},
                'fpar': {}
                },

        ###########################
        ### QEC Carbon Control ####
        ###########################

        'MBI_single_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and one Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_single_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],
                    ['C13_MBI_threshold'           ,   1],
                    ['C13_MBI_RO_duration'            ,  10],
                    ['SP_duration_after_C13'       ,  25],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['E_SP_voltage_after_C13_MBI'   , 0.0],
                    ['A_SP_voltage_after_C13_MBI'   , 0.0],
                    ['E_C13_MBI_RO_voltage'            , 0.0],


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'MBI_multiple_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and one Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_multiple_lt2.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],  #1
                    ['AWG_done_DI_channel'         ,   9],  #2
                    ['SP_E_duration'               , 100],  #3
                    ['wait_after_pulse_duration'   ,   1],  #4
                    ['repetitions'                 ,1000],  #5
                    ['sweep_length'                ,  10],  #6
                    ['cycle_duration'              , 300],  #7  #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],  #8
                    ['MBI_duration'                ,   1],  #9
                    ['max_MBI_attempts'            ,   1],  #10
                    ['nr_of_ROsequences'           ,   1],  #11
                    ['wait_after_RO_pulse_duration',   3],  #12
                    ['N_randomize_duration'        ,  50],  #13

                    ['Nr_C13_init'                 ,  2],   #14
                    ['Nr_MBE'                      ,  1],   #15
                    ['Nr_parity_msmts'             ,  0],   #16
                      #Thresholds
                    ['MBI_threshold'               ,  1],   #17
                    # ['C13_MBI_threshold'           ,  0],   #18
                    ['MBE_threshold'               ,  1],   #19
                    ['Parity_threshold'            ,  1],   #20
                    # Durations
                    ['C13_MBI_RO_duration'         , 30],   #21
                    ['SP_duration_after_C13'       , 25],   #22

                    ['MBE_RO_duration'             ,  10],  #23
                    ['SP_duration_after_MBE'       ,  25],  #24

                    ['Parity_RO_duration'          ,  100],  #25
                    ['C13_MBI_RO_state'              ,  0 ],  #26
                    #Shutter
                    ['use_shutter'                 ,   0], #26 (the real 26 as 17 is commented out)
                    ['Shutter_channel'             ,   4], #27
                    ['Shutter_rise_time'           ,    3000], #28   
                    ['Shutter_fall_time'           ,    3000], #29
                    ['Shutter_safety_time'           ,  200000], #30
                    ],

                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8], #1
                    ['Ex_MBI_voltage'               , 0.8], #2
                    ['Ex_N_randomize_voltage'       , 0.0], #3
                    ['A_N_randomize_voltage'        , 0.0], #4
                    ['repump_N_randomize_voltage'   , 0.0], #5
                    ['E_C13_MBI_RO_voltage'         , 0.0], #6
                    ['E_SP_voltage_after_C13_MBI'   , 0.0], #7
                    ['A_SP_voltage_after_C13_MBI'   , 0.0], #8

                    ['E_MBE_RO_voltage'           , 1e-9], #9
                    ['A_SP_voltage_after_MBE'     , 15e-9],#10
                    ['E_SP_voltage_after_MBE'     , 0e-9], #11

                    ['E_Parity_RO_voltage'        , 1e-9], #12


                    # TODO_MAR: Add voltages for MBE and Parity


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'N_MBI_attempts' : 24,  #attempts since CR check, in success run
                    'N_MBI_starts' : 25,
                    'N_MBI_success' : 28,
                    'ssro_results' : 27,
                    'C13_MBI_starts' : 29,
                    'C13_MBI_success' : 32,
                    'C13_MBE_starts' : 41,
                    'C13_MBE_success': 42,
                    'parity_RO_results': 43,
                    },
                },

        }

config['adwin_lt3_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'green_aom' : 4,
        'yellow_aom' : 5,
        'matisse_aom' : 6,
        'newfocus_aom': 7,
        'gate' : 8,
        'gate_mod' : 9,
        'yellow_aom_frq':10,
        'lock_aom':11,
        'pulse_aom_frq':12,
        }

config['adwin_lt3_dios'] = {

        }

config['adwin_pro_processes'] = {

        'linescan' : {

            'index' : 2,
            'file' : 'linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'SetDac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'Set_TTL_Outputs.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'get_dio' :  {
            'index' : 4,
            'file' : 'Get_TTL_states.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },

        'cr_linescan' : {
            'index' : 2,
            'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
            'file' : 'linescan_cr.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                'activate_scan': 59,
                },
            'params_long': {},
            'params_long_index':20,
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'params_float': {},
            'params_float_index': 21,
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
        },

 # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr.inc',
            'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76,
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
            'params_long_index'  : 30,
            'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
            'params_float_index'  : 31,
            'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },

         'cr_check_mod' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_mod.inc',
            'par' : {
                    'CR_preselect'              : 75,
                    'CR_probe'                  : 68,
                    'CR_repump'                 : 69,
                    'total_CR_counts'           : 70,
                    'noof_repumps'              : 71,
                    'noof_cr_checks'            : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts'             : 76,
                    'repump_mod_activate'       : 66,
                    'cr_mod_activate'           : 67,
                    },
                    'fpar' : {
                    'repump_mod_err' : 78,
                    'cr_mod_err'     : 79,


                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ['repump_mod_DAC_channel'      ,   7],
                    ['cr_mod_DAC_channel'          ,   8],
                    #['counter_ch_input_pattern'    ,   0]
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'           ,   0.8],
                    ['repump_off_voltage'       ,  0.07],
                    ['Ex_CR_voltage'            ,   0.8],
                    ['A_CR_voltage'             ,   0.8],
                    ['Ex_off_voltage'           ,   0.0],
                    ['A_off_voltage'            , -0.08],
                    ['repump_mod_control_offset',   0.0],
                    ['repump_mod_control_amp'   ,   0.0],
                    ['cr_mod_control_offset'    ,   0.0],
                    ['cr_mod_control_amp'       ,   0.0],
                    ['cr_mod_control_avg_pts'   ,   100000.],
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },

         # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check_pos_scan' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_mod_pos_scan.inc',
            'par' : {
                'CR_preselect'              : 75,
                'CR_probe'                  : 68,
                'CR_repump'                 : 69,
                'total_CR_counts'           : 70,
                'noof_repumps'              : 71,
                'noof_cr_checks'            : 72,
                'cr_below_threshold_events' : 79,
                'repump_counts'             : 76,
                'repump_mod_activate'       : 66,
                'cr_mod_activate'           : 67,
                'cur_pos_scan_dac'          : 64,#0 do deactivate
                'cr_per_pos_step'           : 65,
                'activate_position_scan'    : 59,
                },
            'fpar' : {
                'repump_mod_err' : 78,
                'cr_mod_err'     : 79,
                'pos_mod_err'    : 77,

                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                ['counter_channel'             ,   1],
                ['repump_laser_DAC_channel'    ,   7],
                ['Ex_laser_DAC_channel'        ,   6],
                ['A_laser_DAC_channel'         ,   8],
                ['repump_duration'             ,   5],
                ['CR_duration'                 ,  50],
                ['cr_wait_after_pulse_duration',   1],
                ['CR_preselect'                ,  10],
                ['CR_probe'                    ,  10],
                ['CR_repump'                   ,  10],
                ['repump_mod_DAC_channel'      ,   7],
                ['cr_mod_DAC_channel'          ,   8],
                ['pos_mod_scan_length'         , 100],
                ],
            'params_long_index'  : 30,
            'params_float' : [
                ['repump_voltage'           ,   0.8],
                ['repump_off_voltage'       ,  0.07],
                ['Ex_CR_voltage'            ,   0.8],
                ['A_CR_voltage'             ,   0.8],
                ['Ex_off_voltage'           ,   0.0],
                ['A_off_voltage'            , -0.08],
                ['repump_mod_control_offset',   0.0],#V
                ['repump_mod_control_amp'   ,   0.0],#V
                ['cr_mod_control_offset'    ,   0.0],#V
                ['cr_mod_control_amp'       ,   0.0],#V
                ['pos_mod_atto_x'           ,    0.],#auto set
                ['pos_mod_atto_y'           ,    0.],#auto set
                ['pos_mod_atto_z'           ,    0.],#auto set
                ],
            'params_float_index'  : 31,
            'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
            'data_float' : {
                    'atto_positions' : 16,
                    'scan_array' : 17,
                    }
                },
        # ADwin SSRO. This process can not run stand-alone and should be included in another adwin script/process
        # For now all parameters are passed from the other ADwin script/process, this seems more flexible to me.
        # Not sure if this function is then needed. - Machiel 30-12-'13'
        'ssro' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'ssro_pro.inc',
            'par' : {
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    },
                },

        # ADwin single-shot readout
        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot.tb9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,  8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt3.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   19],  
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],

                    #Shutter
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4], 
                    ['Shutter_rise_time'           ,    3000],    
                    ['Shutter_fall_time'           ,    3000], 
                    ['Shutter_safety_time'          ,  50000],
                    ],
                    
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['A_SP_voltage_before_MBI'      , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 84,
                    'current mode': 87,
                    'MBI start': 88,
                    'ROseq_cntr': 90,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'MBI_multiple_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and multiple Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_multiple.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],  #1
                    ['AWG_done_DI_channel'         ,   8],  #2
                    ['SP_E_duration'               , 100],  #3
                    ['wait_after_pulse_duration'   ,   1],  #4
                    ['repetitions'                 ,1000],  #5
                    ['sweep_length'                ,  10],  #6
                    ['cycle_duration'              , 300],  #7   #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],  #8
                    ['MBI_duration'                ,   1],  #9
                    ['max_MBI_attempts'            ,   1],  #10
                    ['nr_of_ROsequences'           ,   1],  #11
                    ['wait_after_RO_pulse_duration',   3],  #12
                    ['N_randomize_duration'        ,  50],  #13

                    ['Nr_C13_init'                 ,  2],   #14
                    ['Nr_MBE'                      ,  1],   #15
                    ['Nr_parity_msmts'             ,  0],   #16
                      #Thresholds
                    ['MBI_threshold'               ,  1],   #17
                    # ['C13_MBI_threshold'           ,  0],   #18
                    ['MBE_threshold'               ,  1],   #19
                    ['Parity_threshold'            ,  1],   #20
                    # Durations
                    ['C13_MBI_RO_duration'         , 30],   #21
                    ['SP_duration_after_C13'       , 25],   #22

                    ['MBE_RO_duration'             ,  10],  #23
                    ['SP_duration_after_MBE'       ,  25],  #24

                    ['Parity_RO_duration'          ,  100],  #25
                    ['C13_MBI_RO_state'              ,  0 ],  #26
                    #Shutter
                    ['use_shutter'                 ,   0], #26 (the real 26 as 17 is commented out)
                    ['Shutter_channel'             ,   4], #27
                    ['Shutter_rise_time'           ,    3000], #28   
                    ['Shutter_fall_time'           ,    3000], #29
                    ['Shutter_safety_time'           ,  200000], #30
                    ],

                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8], #1
                    ['Ex_MBI_voltage'               , 0.8], #2
                    ['Ex_N_randomize_voltage'       , 0.0], #3
                    ['A_N_randomize_voltage'        , 0.0], #4
                    ['repump_N_randomize_voltage'   , 0.0], #5
                    ['E_C13_MBI_RO_voltage'         , 0.0], #6
                    ['E_SP_voltage_after_C13_MBI'   , 0.0], #7
                    ['A_SP_voltage_after_C13_MBI'   , 0.0], #8

                    ['E_MBE_RO_voltage'           , 1e-9], #9
                    ['A_SP_voltage_after_MBE'     , 15e-9],#10
                    ['E_SP_voltage_after_MBE'     , 0e-9], #11

                    ['E_Parity_RO_voltage'        , 1e-9], #12


                    # TODO_MAR: Add voltages for MBE and Parity


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'N_MBI_attempts' : 24,  #attempts since CR check, in success run
                    'N_MBI_starts' : 25,
                    'N_MBI_success' : 28,
                    'ssro_results' : 27,
                    'C13_MBI_starts' : 29,
                    'C13_MBI_success' : 32,
                    'C13_MBI_threshold_list': 40,
                    'C13_MBE_starts' : 41,
                    'C13_MBE_success': 42,
                    'parity_RO_results': 43,
                    },
                },


        'bell_lt3' : {
                'index' : 9,
                'file' : 'bell_lt3.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_done_DI_channel'         ,   17],
                    ['AWG_success_DI_channel'         ,  17],
                    ['SP_duration'                 , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['remote_CR_DO_channel'        ,  15],
                    ['SSRO_duration'               ,  50],
                    ['wait_for_AWG_done'           ,   1],
                    ['sequence_wait_time'          ,  10],
                    ['wait_before_RO'              ,  10],
                    ['invalid_data_marker_do_channel', 5],
                    ['rnd_output_di_channel'       ,  19],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'        , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'        , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'local_mode': 61,
                    'timeout_events': 62,
                    'stop_flag': 63,
                    'completed_reps' : 73,
                    'entanglement_events': 77,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'CR_timer': 27,
                    'CR_hist':  28,
                    },
                },
        'bell_lt4' : {
                'index' : 9,
                'file' : 'bell_lt4.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16], #DX
                    ['AWG_done_DI_channel'         ,   8], #DX
                    ['SP_duration'                 , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['remote_CR_DI_channel'        ,   8],
                    ['SSRO_duration'               ,  50],
                    ['wait_for_AWG_done'           ,   1],
                    ['sequence_wait_time'          ,  10],
                    ['PLU_DI_channel'              ,   1],
                    ['do_sequences'                ,   1],
                    ['wait_for_remote_CR'          ,   1],
                    ['wait_before_RO'              ,  10],
                    ['invalid_data_marker_do_channel', 5],
                    ['rnd_output_di_channel'       ,  19],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'        , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'        , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'remote_mode': 60,
                    'local_mode': 61,
                    'timeout_events': 62,
                    'stop_flag': 63,
                    'completed_reps' : 73,
                    'entanglement_events': 77,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    'CR_timer': 27,
                    'CR_hist':  28,
                    },
                },
                # one CR check followed by multiple times SP-AWG seg-SSRO-repump-delaytime

        'purification' : {
                'index' : 9,
                'file' : 'purification.TB9',
                'include_cr_process' : 'cr_check_mod', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['cycle_duration'                  ,   1],
                    ['SP_duration'                     ,   5],
                    ['wait_after_pulse_duration'       , 100],
                    ['MBI_attempts_before_CR'          ,   1], 
                    ['Dynamical_stop_ssro_threshold'   ,   1], 
                    ['Dynamical_stop_ssro_duration'    ,  20], 
                    ['is_master'                       ,   1], 
                    ['is_two_setup_experiment'         ,   1], 
                    ['do_carbon_init'                  ,   1], # goes to mbi sequence, ends with tomography
                    ['do_C_init_SWAP_wo_SSRO'          ,   1],
                    ['do_swap_onto_carbon'             ,   1],
                    ['do_SSRO_after_electron_carbon_SWAP', 0],
                    ['do_LDE_2'                        ,   1],
                    ['do_phase_correction'             ,   1],
                    ['do_purifying_gate'               ,   1],
                    ['do_carbon_readout'               ,   1],
                    ['PLU_event_di_channel'            ,   0], 
                    ['PLU_which_di_channel'            ,   0], 
                    ['AWG_start_DO_channel'            ,   0], 
                    ['AWG_done_DI_channel'             ,   0],
                    ['wait_for_awg_done_timeout_cycles',   0], 
                    ['AWG_event_jump_DO_channel'       ,   0], 
                    ['AWG_repcount_DI_channel'         ,   0], 
                    ['remote_adwin_di_success_channel' ,   1], 
                    ['remote_adwin_di_fail_channel'    ,   1], 
                    ['remote_adwin_do_success_channel' ,   1], 
                    ['remote_adwin_do_fail_channel'    ,   1], 
                    ['adwin_comm_safety_cycles'        ,   1], 
                    ['adwin_comm_timeout_cycles'       ,   1], 
                    ['remote_awg_trigger_channel'      ,   1],
                    ['invalid_data_marker_do_channel'  ,   1],  
                    ['repetitions'                     ,   0],  
                    ['C13_MBI_RO_duration'             ,  25],   
                    ['master_slave_awg_trigger_delay'  ,   1], # times 10ns  
                    ['phase_correct_max_reps'          ,   5],   
                    ['PLU_during_LDE'                  ,   1],
                    ['pts'                             ,   1],

                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['E_C13_MBI_RO_voltage' , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ['phase_per_sequence_repetition'    , 0.],
                    ['phase_per_compensation_repetition', 0.],
                    ['phase_feedback_resolution'        , 4.5],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'remote_mode': 60,
                    'local_mode': 61,
                    'timeout_events': 62,
                    'stop_flag': 63,
                    'completed_reps' : 73,
                    'entanglement_events': 77,
                    },
                'data_long' : {
                    'CR_before'      : 22,
                    'CR_after'       : 23,
                    # 'C13_MBI_starts'   : 24,  # number of MBI attempts
                    # 'C13_MBI_attempts' : 25,  # number of MBI attempts needed in the successful cycle
                    # 'SSRO_result_after_Cinit'   : 27, # SSRO result after mbi / swap step
                    'SP_hist'                   : 29,    #SP histogram
                    'Phase_correction_repetitions' : 100, # time needed until mbi success (in process cycles)
                    'adwin_communication_time'  : 101,  #time spent for communication between adwins
                    'counted_awg_reps'          : 102,  #Information of how many awg repetitions passed between events (-1)
                    'attempts_first'            : 103,  # number of repetitions until the first succesful entanglement attempt
                    'attempts_second'           : 104, # number of repetitions after swapping until the second succesful entanglement attempt
                    # 'SSRO_after_electron_carbon_SWAP_result' : 37,  # SSRO_after_electron_carbon_SWAP_result
                    'electron_readout_result'   : 105,  # electron readout, e.g. after purification step
                    'carbon_readout_result'     : 106, # SSRO counts final spin readout after tomography
                    'ssro_results'              : 107, # result of the last ssro in the adwin
                    'sync_number'               : 108, # current sync number to compare with HydraHarp data
                    },
                },
        }


config['adwin_telecom_dacs'] = {
        'temperature_control' : 1,
        }

config['adwin_telecom_processes'] = {

        'set_dac' :  {
            'index' : 3,
            'file' : 'SetDac.T93',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },


        'read_adc' :  {
            'index' : 7,
            'file' : 'Read_ADC.T97',
            'par' : {
                'adc_no' : 21,
                },
            'fpar' : {
                'adc_voltage' : 21,
                'apd_counts' : 14,
                },
            },
        }


config['adwin_rt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'green_aom': 4,
        'telecom_delta_temperature': 8
        }


config['adwin_rt2_adcs'] = {
        'telecom_temperature': 2
        }

config['adwin_rt2_dios'] = {

        }

config['adwin_rt2_processes'] = {

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },


        'linescan' : {

            'index' : 2,
            'file' : 'rt2_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {

            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'rt2_simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'rt2_set_dac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'rt2_set_ttl_outputs.TB4',
            'par' : {
                'dio_no' : 61,
                'dio_val' : 62,
                },
            },

        'read_adc' :  {
            'index' : 1,
            'file' : 'rt2_readADC.TB1',
            'par' : {
                'adc_no' : 21,
                },
            'fpar' : {
                'adc_voltage' : 21,
                },
            },


        'trigger_dio' : {
            'index' : 4,
            'file' : 'rt2_dio_trigger.tb4',
            'par' : {
                'dio_no' : 61,
                'startval' : 62, # where to start - 0 or 1
                'waittime' : 63, # length of the trigger pulse in units of 10 ns
            },
        },
    }

config['adwin_lt4_dacs'] = { #TODO describe
        'atto_x' : 1, #D
        'atto_y' : 2, #D
        'atto_z' : 3, #D
        'green_aom' : 4, #D
        'yellow_aom' : 5, #D
        'matisse_aom' : 6, #D
        'newfocus_aom': 7, #D
        'gate' : 8, #D
        'gate_2' : 9, #D
        'gate_mod': 10, #D
        'yellow_aom_frq':11, #D
        }

config['adwin_m1_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'green_aom' : 4,
        'newfocus_aom' : 5,
        'DLPro_aom' : 6,      
        'DLpro_frq': 7,        #not currently used
        'newfocus_frq': 8,
        }
config['adwin_m1_processes'] = {

        'linescan' : {

            'index' : 2,
            'file' : 'linescan.TC2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'simple_counting.TC1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'SetDac.TC3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'Set_TTL_Outputs.TC4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'get_dio' :  {
            'index' : 4,
            'file' : 'Get_TTL_states.TC4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TC5',
            },

        'singleshot' : {
                'index' : 9,
                'file' : 'singleshot_lt2.TC9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'par' : {
                    'completed_reps' : 73,
                    'ssro_counts' : 74,
                    },
                'fpar' : {
                    },
                'params_long' : [
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['Shutter_channel'             ,   4],
                    ],
                'params_long_index'  : 20,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

               # ADwin CR check. This process can not run stand-alone and should be included in another adwin script/process
        'cr_check' : {
            'no_process_start': 'prevent automatic generation of start functions for this process',
            'index' : 999,
            'file' : 'cr_pro.inc',
            'par' : {
                    'CR_preselect'  : 75,
                    'CR_probe'      : 68,
                    'total_CR_counts': 70,
                    'noof_repumps'   : 71,
                    'noof_cr_checks' : 72,
                    'cr_below_threshold_events' : 79,
                    'repump_counts' : 76,
                    },
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['counter_channel'             ,   1],
                    ['repump_laser_DAC_channel'    ,   7],
                    ['Ex_laser_DAC_channel'        ,   6],
                    ['A_laser_DAC_channel'         ,   8],
                    ['repump_duration'             ,   5],
                    ['CR_duration'                 ,  50],
                    ['cr_wait_after_pulse_duration',   1],
                    ['CR_preselect'                ,  10],
                    ['CR_probe'                    ,  10],
                    ['CR_repump'                   ,  10],
                    ],
                'params_long_index'  : 30,
                'params_float' : [
                    ['repump_voltage'       , 0.8],
                    ['repump_off_voltage'   , 0.07],
                    ['Ex_CR_voltage'        , 0.8],
                    ['A_CR_voltage'         , 0.8],
                    ['Ex_off_voltage'       , 0.0],
                    ['A_off_voltage'        , -0.08]
                    ],
                'params_float_index'  : 31,
                'data_long' : {
                    'CR_before' : 22,
                    'CR_after' : 23,
                    'statistics' : 26,
                    },
                },

        'MBI' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one MBI step and can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'MBI_lt2.TC9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],
                    ['MBI_duration'                ,   1],
                    ['max_MBI_attempts'            ,   1],
                    ['MBI_threshold'               ,   0],
                    ['nr_of_ROsequences'           ,   1],
                    ['wait_after_RO_pulse_duration',   3],
                    ['N_randomize_duration'        ,  50],

                    #Shutter
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4], 
                    ['Shutter_rise_time'           ,    3000],    
                    ['Shutter_fall_time'           ,    3000], 
                    ['Shutter_safety_time'          ,  200000],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8],
                    ['Ex_MBI_voltage'               , 0.8],
                    ['Ex_N_randomize_voltage'       , 0.0],
                    ['A_N_randomize_voltage'        , 0.0],
                    ['repump_N_randomize_voltage'   , 0.0],
                    ['A_SP_voltage_before_MBI'      , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'MBI_attempts' : 24,
                    'MBI_cycles' : 25,
                    'ssro_results' : 27,
                    'MBI_time' : 28,
                    },
                },

        'integrated_ssro' : {
                'index' : 9,
                'file' : 'integrated_ssro_lt2.TC9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['SP_filter_duration'          ,   0],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300], #on T11 processor 300 corresponds to 1us
                    ['sweep_length'                ,   1],
                    ['wait_after_RO_pulse_duration',1],
                    ['use_shutter'                 ,   0],
                    ['Shutter_channel'             ,   4],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 25,
                'params_float' : [
                    ['Ex_SP_voltage'        , 0.8],
                    ['A_SP_voltage'         , 0.8],
                    ['Ex_RO_voltage'        , 0.8],
                    ['A_RO_voltage'         , 0.8],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 10,
                'par' : {
                    'completed_reps' : 73,
                    },
                'data_long' : {
                    'SP_hist' : 24,
                    'RO_data' : 25,
                    },
                },

        'MBI_multiple_C13' : {
                'info' : """
                    Conditional repumping, and resonant readout at the end.
                    Has one Nitrogen-MBI step and one Carbon-MBI step, can read out multiple times (e.g., on different lines).
                    """,
                'index' : 9,
                'file' : 'C13_multiple_lt2.TC9',
                'include_cr_process' : 'cr_check', # This process includes the CR check lib
                'params_long' : [                  # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],  #1
                    ['AWG_done_DI_channel'         ,   9],  #2
                    ['SP_E_duration'               , 100],  #3
                    ['wait_after_pulse_duration'   ,   1],  #4
                    ['repetitions'                 ,1000],  #5
                    ['sweep_length'                ,  10],  #6
                    ['cycle_duration'              , 300],  #7  #on T11 processor 300 corresponds to 1us
                    ['AWG_event_jump_DO_channel'   ,   6],  #8
                    ['MBI_duration'                ,   1],  #9
                    ['max_MBI_attempts'            ,   1],  #10
                    ['nr_of_ROsequences'           ,   1],  #11
                    ['wait_after_RO_pulse_duration',   3],  #12
                    ['N_randomize_duration'        ,  50],  #13

                    ['Nr_C13_init'                 ,  2],   #14
                    ['Nr_MBE'                      ,  1],   #15
                    ['Nr_parity_msmts'             ,  0],   #16
                      #Thresholds
                    ['MBI_threshold'               ,  1],   #17
                    # ['C13_MBI_threshold'           ,  0],   #18
                    ['MBE_threshold'               ,  1],   #19
                    ['Parity_threshold'            ,  1],   #20
                    # Durations
                    ['C13_MBI_RO_duration'         , 30],   #21
                    ['SP_duration_after_C13'       , 25],   #22

                    ['MBE_RO_duration'             ,  10],  #23
                    ['SP_duration_after_MBE'       ,  25],  #24

                    ['Parity_RO_duration'          ,  100],  #25
                    ['C13_MBI_RO_state'              ,  0 ],  #26
                    #Shutter
                    ['use_shutter'                 ,   0], #26 (the real 26 as 17 is commented out)
                    ['Shutter_channel'             ,   4], #27
                    ['Shutter_rise_time'           ,    3000], #28   
                    ['Shutter_fall_time'           ,    3000], #29
                    ['Shutter_safety_time'           ,  200000], #30
                    ],

                'params_long_index'  : 20,
                'params_long_length' : 100,
                'params_float' : [
                    ['Ex_SP_voltage'                , 0.8], #1
                    ['Ex_MBI_voltage'               , 0.8], #2
                    ['Ex_N_randomize_voltage'       , 0.0], #3
                    ['A_N_randomize_voltage'        , 0.0], #4
                    ['repump_N_randomize_voltage'   , 0.0], #5
                    ['E_C13_MBI_RO_voltage'         , 0.0], #6
                    ['E_SP_voltage_after_C13_MBI'   , 0.0], #7
                    ['A_SP_voltage_after_C13_MBI'   , 0.0], #8

                    ['E_MBE_RO_voltage'           , 1e-9], #9
                    ['A_SP_voltage_after_MBE'     , 15e-9],#10
                    ['E_SP_voltage_after_MBE'     , 0e-9], #11

                    ['E_Parity_RO_voltage'        , 1e-9], #12
                    # TODO_MAR: Add voltages for MBE and Parity


                    ],
                'params_float_index'  : 21,
                'params_float_length' : 100,
                'par' : {
                    'completed_reps' : 73,
                    'MBI failed' : 74,
                    'current mode': 77,
                    'MBI start': 78,
                    'ROseq_cntr': 80,
                    },
                'data_long' : {
                    'N_MBI_attempts' : 24,  #attempts since CR check, in success run
                    'N_MBI_starts' : 25,
                    'N_MBI_success' : 28,
                    'ssro_results' : 27,
                    'C13_MBI_starts' : 29,
                    'C13_MBI_success' : 32,
                    'C13_MBE_starts' : 41,
                    'C13_MBE_success': 42,
                    'parity_RO_results': 43,
                    },
                },

}

config['adwin_rt1_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        }

config['adwin_rt1_dios'] = {

        }

config['adwin_rt1_processes'] = {

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },


        'linescan' : {

            'index' : 2,
            'file' : 'rt1_linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'counter' : {

            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'rt1_simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'rt1_set_dac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'rt1_set_ttl_outputs.TB4',
            'par' : {
                'dio_no' : 61,
                'dio_val' : 62,
                },
            },

        'trigger_dio' : {
            'index' : 4,
            'file' : 'rt1_dio_trigger.tb4',
            'par' : {
                'dio_no' : 61,
                'startval' : 62, # where to start - 0 or 1
                'waittime' : 63, # length of the trigger pulse in units of 10 ns
            },
        },
    }


config['adwin_cav1_dacs'] = {
        'jpe_fine_tuning_1': 1,
        'jpe_fine_tuning_2': 2,
        'jpe_fine_tuning_3': 3,
        'green_aom' : 4,
        'newfocus_freqmod': 5,
        'scan_mirror_x' : 6,
        'scan_mirror_y': 7,
        }

config['adwin_cav1_dios'] = {
        }

config['adwin_cav1_adcs'] = {
        'photodiode': 16,
        'photodiode_ref': 32,
        }

config['adwin_cav1_dios'] = {
        'montana_sync_ch': 21,
        }


config['adwin_cav1_processes'] = {

        'counter' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'simple_counting.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'photodiode_readout' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 1,
            'file' : 'photodiode_readout.TB1',
            'par' : {
                'set_integration_time' : 23,
                'set_avg_periods' : 24,
                'set_single_run' : 25,
                'get_countrates' : [41, 42, 43, 44],
                },
            'data_long' : {
                'get_last_counts' : 45,
                },
            },

        'linescan' : {

            'index' : 2,
            'file' : 'linescan.TB2',
            'par' : {
                'set_cnt_dacs' : 1,
                'set_steps' : 2,
                'set_px_action' : 3,
                'get_px_clock' : 4,
                },
            'fpar' : {
                'set_px_time' : 1,
                'supplemental_data_input' : 2,
                'simple_counting' : 3,  # 1 for simple, 0 for resonant counting
                },
            'data_long' : {
                'set_dac_numbers' : 200,
                'get_counts' : [11,12,13],
                },
            'data_float' : {
                'set_start_voltages' : 199,
                'set_stop_voltages' : 198,
                'get_supplemental_data' : 15,
                },
            },

        'set_dac' :  {
            'index' : 3,
            'file' : 'SetDac.TB3',
            'par' : {
                'dac_no' : 20,
                },
            'fpar' : {
                'dac_voltage' : 20,
                },
            },

        'read_adc' :  {
            'index' : 6,
            'file' : 'readADC.TB6',
            'par' : {
                'adc_no' : 21,
                },
            'fpar' : {
                'adc_voltage' : 21,
                },
            },

        'set_dio' :  {
            'index' : 4,
            'file' : 'Set_TTL_Outputs.TB4',
            'par' : {
                'dio_no' : 61, #configured DIO 08:15 as input, all other ports as output
                'dio_val' : 62,
                },
            },

        'init_data' :  {
            'index' : 5,
            'file' : 'init_data.TB5',
            },

        'timeseries_photodiode' : {
            'index' : 2,
            'file' : 'timeseries_photodiode.TB2',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['ADC_channel'                 ,   1],
                    ['ADC_ref_channel'             ,   2],
                    ['nr_steps'                    ,   1],
                    ['wait_cycles'                 ,   1],
                    ],
                'params_long_index'  : 200,
                'params_long_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage' : 11,
                    'photodiode_reference' : 12,
                    },
                'data_long' : {
                    'timer' : 13,
                    },

            },


        'laserscan_photodiode' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 2,
            'file' : 'voltagescan_photodiode.TB2',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['DAC_channel'                 ,   8],
                    ['ADC_channel'                 ,   1],
                    ['nr_steps'                    ,   1],
                    ['wait_cycles'                 ,  50],
                    ],
                'params_long_index'  : 200,
                'params_long_length' : 8,
                'params_float' : [
                    ['start_voltage'               , 0.0],
                    ['voltage_step'               , 0.01],
                    ],
                'params_float_index'  : 199,
                'params_float_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage' : 11,
                    },
            },

        'fine_piezo_jpe_scan' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 2,
            'file' : 'fine_piezo_jpe_scan.TB2',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['DAC_ch_fpz1'                 ,   0],
                    ['DAC_ch_fpz2'                 ,   0],
                    ['DAC_ch_fpz3'                 ,   0],
                    ['ADC_channel'                 ,   1],
                    ['ADC_ref_channel'             ,   2],
                    ['nr_steps'                    ,   1],
                    ['wait_cycles'                 ,  50],
                    ['use_counter'                 ,   0],
                    ],
                'params_long_index'  : 200,
                'params_long_length' : 8,
                'params_float' : [
                    ['start_voltage_1'            , 0.0],
                    ['start_voltage_2'            , 0.0],
                    ['start_voltage_3'            , 0.0],
                    ['voltage_step'               , 0.01],
                    ],
                'params_float_index'  : 199,
                'params_float_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage' : 11,
                    'photodiode_reference' : 12,
                    },
            },

        'fine_piezo_jpe_scan_sync' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 2,
            'file' : 'fine_piezo_jpe_scan_sync.TB2',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['DAC_ch_fpz1'                 ,   0],
                    ['DAC_ch_fpz2'                 ,   0],
                    ['DAC_ch_fpz3'                 ,   0],
                    ['ADC_channel'                 ,   1],
                    ['montana_sync_channel'        ,   1],
                    ['nr_steps'                    ,   1],
                    ['nr_scans'                    ,   1],                    
                    ['wait_cycles'                 ,  50],
                    ['delay_us'                    ,   0],
                    ],
                'params_long_index'  : 200,
                'params_long_length' : 8,
                'params_float' : [
                    ['start_voltage_1'            , 0.0],
                    ['start_voltage_2'            , 0.0],
                    ['start_voltage_3'            , 0.0],
                    ['voltage_step'               , 0.01],
                    ],
                'params_float_index'  : 199,
                'params_float_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage' : 11,
                    },
                'data_long'   : {
                    'timestamps' : 12,
                },
            },

        'voltage_scan_sync' : {
            'index' : 5,
            'file' : 'voltage_scan_sync.TB5',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['DAC_ch_1'                    ,   0],
                    ['DAC_ch_2'                    ,   0],
                    ['DAC_ch_3'                    ,   0],
                    ['ADC_channel'                 ,   1],
                    ['use_sync'                    ,   0],
                    ['sync_ch'                     ,   1],
                    ['nr_steps'                    ,   1],
                    ['nr_scans'                    ,   1],                    
                    ['wait_cycles'                 ,  50],
                    ['delay_us'                    ,   0],
                    ['ADC_averaging_cycles'        ,   50],
                    ['scan_auto_reverse'           ,   50],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 15,
                'params_float' : [
                    ['start_voltage_1'            ,  0.0],
                    ['start_voltage_2'            ,  0.0],
                    ['start_voltage_3'            ,  0.0],
                    ['voltage_step'               , 0.01],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage' : 11,
                    'laser_frequency' : 13,
                    },
                'data_long'   : {
                    'timestamps' : 12,
                },
            },


        'widerange_laserscan' : {
            'doc' : '',
            'info' : {
                'counters' : 4,
                },
            'index' : 2,
            'file' : 'longrange_laserscan.TB2',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['DAC_coarse_ch'               ,   0],
                    ['DAC_fine_ch'                 ,   0],
                    ['ADC_ch'                      ,   0],
                    ['nr_fine_steps'               ,   1],
                    ['nr_coarse_steps'             ,   1],
                    ['wait_cycles'                 ,   1],
                    ],
                'params_long_index'  : 200,
                'params_long_length' : 8,
                'params_float' : [
                    ['start_coarse_volt'          , 0.0],
                    ['step_size_coarse'           , 0.0],
                    ['start_fine_volt'            , 0.0],
                    ['stop_fine_volt'             , 0.0],
                    ],
                'params_float_index'  : 199,
                'params_float_length' : 8,
                'par' : {
                    },
                'data_float' : {
                    'photodiode_voltage'    : 11,
                    'wavemeter'             : 12,
                    },
            },


        'lockin_dac_adc' : {
            'doc' : '',
            'info' : {
                },
            'index' : 9,
            'file' : 'lockin_dac_adc.TB9',
            'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['output_dac_channel'                ,   0],
                    ['input_adc_channel'                 ,   0],
                    ['modulation_bins'                   ,   0],
                     ['error_averaging'                  ,   0],
                    ],
                'params_long_index'  : 20,
                'params_long_length' : 3,
                'params_float' : [
                    ['modulation_amplitude'          , 0.0],
                    ['modulation_frequency'           , 0.0],
                    ],
                'params_float_index'  : 21,
                'params_float_length' : 2,
                'par' : {

                    },
                'fpar' : {
                    'dac_voltage_offset' : 71,
                    'adc_voltage' : 72,
                    'error_signal': 73,
                },
                'data_float' : {
                    'modulation'    : 24,
                    'adc_mod'       : 25,
                    },
            },

        }


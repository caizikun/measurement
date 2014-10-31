config = {}
config['adwin_lt1_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 8,  # dac 3 is no longer working with the ATTO CONTROLLER!
        'yellow_aom_frq': 4,
        'gate_mod' : 5, #not yet connected
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,   0],
                    ['AWG_done_DI_channel'         ,   9],
                    ['SP_E_duration'               , 100],
                    ['wait_after_pulse_duration'   ,   1],
                    ['repetitions'                 ,1000],
                    ['sweep_length'                ,  10],
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
                    ['sweep_length'                ,   1],
                    ['wait_after_RO_pulse_duration',   1],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                'file' : 'adaptive_magnetometry_MBI_lt2.TB9',
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
                    ['cycle_duration'              , 300],
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
                    ['do_MBI'                      ,   0],
                    
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],
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
                    ['cycle_duration'              , 300],  #7
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

                    ['Parity_RO_duration'          ,  10],  #25
                    ['C13_MBI_RO_state'              ,  0 ],  #26

                    ],# TODO_MAR: add to msmt params and make usefull in Adwin 
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
                    ['cycle_duration'              , 300],
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
                    ['AWG_done_DI_channel'         ,   8],
                    ['send_AWG_start'              ,   0],
                    ['wait_for_AWG_done'           ,   0],
                    ['SP_duration'                 , 100],
                    ['sequence_wait_time'          ,   0],
                    ['wait_after_pulse_duration'   ,   1],
                    ['SSRO_repetitions'            ,1000],
                    ['SSRO_duration'               ,  50],
                    ['SSRO_stop_after_first_photon',   0],
                    ['cycle_duration'              , 300],
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

        'bell_lt4' : {
                'index' : 9,
                'file' : 'bell_lt4.TB9',
                'include_cr_process' : 'cr_check', #This process includes the CR check lib
                'params_long' : [           # keep order!!!!!!!!!!!!!
                    ['AWG_start_DO_channel'        ,  16],
                    ['AWG_done_DI_channel'         ,   8],
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
        'bell_lt3' : {
                'index' : 9,
                'file' : 'bell_lt3.TB9',
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



        }


config['adwin_rt2_dacs'] = {
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
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
        'atto_x' : 1,
        'atto_y' : 2,
        'atto_z' : 3,
        'green_aom' : 4,
        'yellow_aom' : 5,
        'matisse_aom' : 6,
        'newfocus_aom': 7,
        'gate' : 8,
        'gate_2' : 9,
        'gate_mod': 10,
        'yellow_aom_frq':11,
        }

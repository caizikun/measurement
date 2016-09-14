ssro.AdwinSSRO.adwin_processes_key = 'adwin_m1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['DLProAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
# ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']


# if qt.exp_params['protocols']['AdwinSSRO']['yellow']:
#     ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
# else:
ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom

pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SGS100A_2']
pulsar_msmt.PulsarMeasurement.mwsrc2 = qt.instruments['SGS100A_1']
pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG']
pulsar_msmt.PulsarMeasurement.physical_adwin = qt.instruments['physical_adwin']
#pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N']
#pq_threaded_measurement.PQ_threaded_Measurement.PQ_ins=qt.instruments['TH_260N']
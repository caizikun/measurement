qt.exp_params=mcfg.cfg

ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt2_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM']
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM']
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']


if qt.exp_params['protocols']['AdwinSSRO']['yellow']:
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
else:
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom

pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SGS100A']
#pulsar_msmt.PulsarMeasurement.mwsrc2 = qt.instruments['noIQ_SMB100']
# pulsar_msmt.PulsarMeasurement.mwsrc2 = qt.instruments['SGS100A']
pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG']
pulsar_msmt.PulsarMeasurement.physical_adwin = qt.instruments['physical_adwin']

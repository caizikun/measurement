print 'loading setup tools...'
from measurement.scripts.lt1_scripts import stools
reload(stools)

print 'reload all modules...'
execfile("D:/measuring/measurement/scripts/lt1_scripts/setup/reload_all.py")

####
print 'reload all measurement parameters and calibrations...'
execfile("D:/measuring/measurement/scripts/lt1_scripts/setup/msmt_params.py")

qt.current_setup='lt1'

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

####
print 'configure the setup-specific hardware...'
ssro.AdwinSSRO.adwin_processes_key = 'adwin_lt1_processes'
ssro.AdwinSSRO.E_aom = qt.instruments['MatisseAOM'] 
ssro.AdwinSSRO.A_aom = qt.instruments['NewfocusAOM'] 
ssro.AdwinSSRO.green_aom = qt.instruments['GreenAOM']
ssro.AdwinSSRO.yellow_aom = qt.instruments['YellowAOM']
ssro.AdwinSSRO.adwin = qt.instruments['adwin']

if qt.cfgman.get('protocols/AdwinSSRO/yellow'):
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.yellow_aom
else:
    ssro.AdwinSSRO.repump_aom = ssro.AdwinSSRO.green_aom


sequence.SequenceSSRO.awg = qt.instruments['AWG']
sequence.SequenceSSRO.mwsrc = qt.instruments['SMB100']
sequence.SequenceSSRO.chan_mwI = 'MW_Imod'
sequence.SequenceSSRO.chan_mwQ = 'MW_Qmod'
sequence.SequenceSSRO.chan_mw_pm = 'MW_pulsemod'
sequence.SequenceSSRO.awgcfg_module = awgcfg
sequence.SequenceSSRO.awgcfg_args = ['mw', 'rf', 'adwin']

mbi.MBIMeasurement.chan_RF  = 'RF' 
mbi.MBIMeasurement.chan_adwin_sync = 'adwin_sync'
mbi.MBIMeasurement.physical_adwin = qt.instruments['physical_adwin']

pulsar_msmt.PulsarMeasurement.awg = qt.instruments['AWG']
pulsar_msmt.PulsarMeasurement.mwsrc = qt.instruments['SMB100']
pulsar_msmt.MBI.physical_adwin = qt.instruments['physical_adwin']

#teleportation.Teleportation.adwin_processes_key = 'adwin_lt1_processes'
#teleportation.Teleportation.E_aom = qt.instruments['Velocity1AOM']
#teleportation.Teleportation.A_aom = qt.instruments['Velocity2AOM']
#teleportation.Teleportation.green_aom = qt.instruments['GreenAOM']
#teleportation.Teleportation.yellow_aom = qt.instruments['YellowAOM']
#teleportation.Teleportation.adwin = qt.instruments['adwin']
####

print 'configure the pulsar sequencer and update pulses and elements...'
execfile("D:/measuring/measurement/scripts/lt1_scripts/setup/sequence.py")



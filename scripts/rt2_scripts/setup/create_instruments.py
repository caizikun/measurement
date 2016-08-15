
physical_adwin = qt.instruments.create('physical_adwin','ADwin_Gold_II',address=1)

adwin = qt.instruments.create('adwin', 'adwin_rt2', 
        physical_adwin='physical_adwin')

# edac40 = qt.instruments.create('edac40','EDAC40',MAC_address='\x00\x04\xA3\x13\xDA\x94')
# okotech_dm = qt.instruments.create('okotech_dm', 'OKOTech_DM',dac=qt.instruments['edac40'])

#powermeter = qt.instruments.create('powermeter','Thorlabs_PM100D', address='USB0::0x1313::0x8078::PM002587::INSTR')#P0007639
powermeter = qt.instruments.create('powermeter','Thorlabs_PM100', address='ASRL2::INSTR')

AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', address='GPIB::1::INSTR',reset=False, numpoints=1e3)

SMB100 = qt.instruments.create('SMB100', 'RS_SMB100', address='GPIB::28::INSTR', reset=False)

counters = qt.instruments.create('counters', 'counters_via_adwin',
        adwin='adwin')

master_of_space = qt.instruments.create('master_of_space', 
        'master_of_space', adwin='adwin', dimension_set='mos_rt2')

linescan_counts = qt.instruments.create('linescan_counts', 
        'linescan_counts',  adwin='adwin', mos='master_of_space',
        counters='counters')

setup_controller = qt.instruments.create('setup_controller',
         'setup_controller',
        use = { 'master_of_space' : 'mos'} )

scan2d = qt.instruments.create('scan2d', 'scan2d_counts',
         linescan='linescan_counts', mos='master_of_space',
        xdim='x', ydim='y', counters='counters', setup_controller='setup_controller')
 
opt1d_counts = qt.instruments.create('opt1d_counts', 
         'optimize1d_counts', linescan='linescan_counts', 
        mos='master_of_space', counters='counters')

optimiz0r = qt.instruments.create('optimiz0r', 'optimiz0r', opt1d_ins=
        opt1d_counts, mos_ins=master_of_space, dimension_set='rt2')

c_optimiz0r = qt.instruments.create('c_optimiz0r', 'convex_optimiz0r', 
    mos_ins=master_of_space, adwin_ins = adwin)

GreenAOM = qt.instruments.create('GreenAOM', 'AOM', 
        use_adwin='adwin', use_pm= 'powermeter')

p7889 = qt.instruments.create('p7889','FastCom_P7889')



# ###############
# # Start setup #
# ###############

# execfile(os.path.join(qt.config['startdir'],'rt2_scripts/setup_rt2.py'))
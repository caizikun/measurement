import os
qt.current_setup='bs'
qt.reload_current_setup = os.path.join(qt.config['startdir'],"bs_scripts/setup_bs.py")

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

print 'reload all modules...'
execfile(os.path.join(qt.config['startdir'],"bs_scripts/setup/reload_all.py"))

####
####
# set all the static variables for lt3
execfile(os.path.join(qt.config['startdir'],'bs_scripts/setup/bs_statics.py'))

### A module for performing magnetic field calculations.
### Examples are conversions between fields and frequencies,
### determining the magnet position and calculating the magnet
### path to a desired magnetic field.

### Import the config manager and NV parameters
import qt
import numpy as np

# reload all parameters and modules
execfile(qt.reload_current_setup)

current_NV = qt.exp_params['samples']['current']
current_prot = qt.exp_params['protocols']['current']

### Import the NV and current esr parameters
ZFS         = qt.exp_params['samples'][current_NV]['zero_field_splitting']
g_factor    = qt.exp_params['samples'][current_NV]['g_factor']
current_f_msm1 = qt.exp_params['samples'][current_NV]['ms-1_cntr_frq']
current_f_msp1 = qt.exp_params['samples'][current_NV]['ms+1_cntr_frq']
current_B_field =  abs(ZFS-current_f_msp1)/g_factor

### Import the magnet parameters
nm_per_step         = qt.exp_params['magnet']['nm_per_step']
radius              = qt.exp_params['magnet']['radius']
thickness           = qt.exp_params['magnet']['thickness']
strength_constant   = qt.exp_params['magnet']['strength_constant']


### Simple conversions
def convert_Bz_to_f(B_field):
    ''' Calculates the (ms=-1, ms=+1) frequencies
    for a given B_field input. Assumes the field is along Z
    '''
    freq_msm1 = ZFS - B_field * g_factor
    freq_msp1 = ZFS + B_field * g_factor
    return freq_msm1, freq_msp1

def convert_f_to_Bz(freq=current_f_msm1):
    ''' Calculates the B_field (z-component only)
    for a given frequency (either ms=-1 or ms=+1).
    Assumes a field along Z'''

    B_field = abs(ZFS-freq)/g_factor
    return B_field

def calc_ZFS(msm1_freq=current_f_msm1, msp1_freq=current_f_msp1):
    ''' calculate the average of the current ESR frequencies '''
    calculated_ZFS = (msm1_freq+msp1_freq)/2
    return calculated_ZFS

### Get the field vector values and magnet position
def get_B_field(msm1_freq=current_f_msm1, msp1_freq=current_f_msp1):
    ''' Returns the (Bz_field, Bx_field) for given given
    ms=-1 and ms=0 frequencies (GHz)
    '''
    msm1_f = msm1_freq
    msp1_f = msp1_freq
    Bz = (msp1_f**2 - msm1_f**2)/(4.*ZFS*g_factor)
    Bx = (abs(msm1_f**2 - (ZFS-g_factor*Bz)**2 )**0.5)/g_factor
    return (Bz, Bx)

def get_magnet_position(msm1_freq=current_f_msm1,msp1_freq = current_f_msp1,ms = 'plus',solve_by = 'list'):
    ''' determines the magnet position (mm) for given msm1_freq
    or msp1_freq (GHz)
    JULIA:  I am not sure yet what will be the best solution: try by measurement'''
    if ms is 'minus':
        B_field = convert_f_to_Bz(freq=msm1_freq)
        print B_field
    if ms is 'plus':
        B_field = convert_f_to_Bz(freq=msp1_freq)
    if solve_by == 'list':
        d = np.linspace(10.4,9.4,10**4+1) # ! this is the right domain for B around 300 G
        B_field_difference = np.zeros(len(d))
        for j in [int(i) for i in np.linspace(0,len(d)-1,len(d))]:
            B_field_difference[j] = abs(B_field-get_field_at_position(d[j]))
        B_field_difference = np.array(B_field_difference).tolist()
        j_index = B_field_difference.index(min(B_field_difference))
        position = d[j_index]
    if solve_by == 'eqn':
        position = 22.2464-0.0763*B_field+1.511e-4*B_field**2-1.1023e-7*B_field**3
    return position

def get_field_at_position(distance):
    ''' returns the field (G) at input distance (mm)'''
    B_field = 1e4* strength_constant/2. * ( (thickness+distance)/(radius**2 +(thickness+distance)**2)**0.5 \
            - distance/(radius**2 + distance**2)**0.5)
    return B_field

def get_freq_at_position(distance):
    ''' returns the freq (GHz) at input distance (mm)'''
    B_field = get_field_at_position(distance)
    Frequency = convert_Bz_to_f(B_field)
    return Frequency

def get_field_gradient(distance):
    ''' returns the field (G) at input distance (mm)'''
    pass

def get_all(freq_ms_m1=current_f_msm1, freq_ms_p1=current_f_msp1):
    '''function that returns all the magnetic field and magnet properties
    for the given or current ms=-1 and ms=+1 frequencies'''
    print 'Given ms-1 transition frequency = '+str(freq_ms_m1*1e-9) +' GHz'
    print 'Given ms+1 transition frequency = '+str(freq_ms_p1*1e-9) + ' GHz'
    average_frq = calc_ZFS(msm1_freq=freq_ms_m1, msp1_freq=freq_ms_p1)
    print '(f_ms=-1 + f_ms=+1)/2 = ' + str(average_frq*1e-9) + ' GHz'
    print 'Zero field splitting  = ' + str(ZFS*1e-9) + ' GHz'
    calculated_B_field = get_B_field(msm1_freq=freq_ms_m1, msp1_freq=freq_ms_p1)
    print 'Current B field = '+str(calculated_B_field)+ ' G'
    calculated_position = get_magnet_position(msm1_freq=freq_ms_m1, msp1_freq=freq_ms_p1,ms = 'plus',solve_by = 'list')
    print 'Current distance between magnet and NV centre = '+ str(calculated_position)+ ' mm'

### Determine where to move

def steps_to_frequency(freq=current_f_msp1,freq_id=current_f_msp1, ms = 'plus'):
    '''determine the steps needed to go to a certain frequency (freq_id)'''

    position = get_magnet_position(msm1_freq=freq,msp1_freq=freq,ms = ms,solve_by = 'list')
    print 'Magnet distance to NV: ' +str(position)
    position_ideal = get_magnet_position(msm1_freq=freq_id,msp1_freq=freq_id,ms = ms,solve_by = 'list')
    print 'Wanted magnet distance to NV: '+ str(position_ideal)
    d_position_nm = (position - position_ideal)*1e6
    d_steps = d_position_nm/nm_per_step
    return d_steps

def steps_to_field(B_field,B_field_id = current_B_field):
    '''determine the steps needed to go to a certain field'''
    freq_msm1, freq_msp1 = convert_Bz_to_f(B_field)
    freq_msm1_id, freq_msp1_id = convert_Bz_to_f(B_field_id)
    d_steps = steps_to_frequency(freq = freq_msp1,freq_id=freq_msp1_id, ms = 'plus')
    return d_steps












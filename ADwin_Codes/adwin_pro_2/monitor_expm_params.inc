'<ADbasic Header, Headerversion 001.001>
'<Header End>
' this program is a simple monitor to pull in some key values that we care about over the duration of the expm.
' PH 2017

#DEFINE max_expm_repetitions 500000

DIM count_index, old_cr_checks, old_cr_counts, old_repumps, old_repump_counts, cr_checks, repumps  as LONG
DIM cr_counts, repump_counts as FLOAT

'return
DIM DATA_40[max_expm_repetitions] AS FLOAT at DRAM_Extern ' Taper freq
DIM DATA_41[max_expm_repetitions] AS FLOAT at DRAM_Extern  ' New Focus freq
DIM DATA_42[max_expm_repetitions] AS FLOAT at DRAM_Extern  ' Yellow freq
DIM DATA_43[max_expm_repetitions] AS FLOAT at DRAM_Extern  ' Gate voltage
DIM DATA_44[max_expm_repetitions] AS FLOAT at DRAM_Extern  ' CR Check counts (last 100 ms)
DIM DATA_45[max_expm_repetitions] AS FLOAT at DRAM_Extern  ' Repump counts (last 100 ms)

DIM Monitor_Initializer[100] as FLOAT AT EM_LOCAL ' this array is used for initialization purposes and stored in the local memory of the adwin 


SUB init_expm_param_monitor()

  count_index = 0
  old_cr_checks = 0
  old_cr_counts = 0
  old_repumps = 0
  old_repump_counts = 0
  FPAR_71 = 0
  FPAR_72 = 0

  '  ' note: the MemCpy function only works for T11 processors.
  '  ' this is a faster way of filling up global data arrays in the external memory. See Adbasic manual
  array_step = 1
  FOR i = 1 TO max_single_click_ent_repetitions/100
    MemCpy(Monitor_Initializer[1],DATA_40[array_step],100)
    MemCpy(Monitor_Initializer[1],DATA_41[array_step],100)
    MemCpy(Monitor_Initializer[1],DATA_42[array_step],100)
    MemCpy(Monitor_Initializer[1],DATA_43[array_step],100)
    MemCpy(Monitor_Initializer[1],DATA_44[array_step],100)
    MemCpy(Monitor_Initializer[1],DATA_45[array_step],100)
    array_step = array_step + 100
  NEXT i
  
ENDSUB

'''' Records the average cr check counts from the last 200 tries
SUB record_cr_counts()

  inc(count_index)
  
  if (count_index = 200) then
    
    cr_checks = Par_72 - old_cr_checks
    cr_counts = Par_70 - old_cr_counts
    old_cr_checks = Par_72
    old_cr_counts = Par_70
    
    ' By construction, this shouldnt ever be the case. But might as well do a quick idiot check
    if (cr_checks = 0) THEN
      FPar_72 = 0
    else 
      FPar_72 = cr_counts/cr_checks
    endif

    repumps = par_71 - old_repumps
    repump_counts = par_76 - old_repump_counts
    old_repumps = par_71
    old_repump_counts = par_76
    
    if (repumps > 0) THEN
      FPar_71 = repump_counts/repumps
    endif
    
    count_index = 0
    
  endif
  
  
  
ENDSUB

SUB record_expm_params(repetition_index)
  DATA_40[repetition_index] = FPar_44
  DATA_41[repetition_index] = FPar_41
  DATA_42[repetition_index] = FPar_42
  DATA_43[repetition_index] = 0 '  To implement
  DATA_44[repetition_index] = FPar_72
  DATA_45[repetition_index] = FPar_71
  
ENDSUB


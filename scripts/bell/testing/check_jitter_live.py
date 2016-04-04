import msvcrt
pharp=qt.instruments['PH_300']
pharp.OpenDevice()
pharp.start_histogram_mode()
pharp.ClearHistMem()
pharp.set_Range(4) # 64 ps binsize
pharp.set_CFDLevel0(50)
pharp.set_CFDLevel1(50)
qt.msleep(1)
pharp.StartMeas(int(4 * 1e3)) #10 second measurement
qt.msleep(10)
print 'starting PicoHarp measurement'
#while pharp.get_MeasRunning():
#    if(msvcrt.kbhit() and msvcrt.getch()=='q'):
#        print 'q pressed, quitting current run'
#        pharp.StopMeas()
#        break
hist=pharp.GetHistogram()
print 'PicoHarp measurement finished'

print '-------------------------------'
ret=''
ret=ret+ str(hist[hist>0])
peaks=np.where(hist>0)[0]*pharp.get_Resolution()/1000.
ret=ret+'\n'+ str(peaks)

peak_loc = 890.1
if len(peaks)>1:
    peaks_width=peaks[-1]-peaks[0]
    peak_max=np.argmax(hist)*pharp.get_Resolution()/1000.
    if (peaks_width)>.5:
        ret=ret+'\n'+ 'JITTERING!! Execute check_awg_triggering with a reset'
        jitterDetected=True
    elif (peak_max<peak_loc-0.25) or (peak_max>peak_loc+0.25):
        ret=ret+'\n'+ 'Warning peak max at unexpected place, PEAK WRONG'
        jitterDetected=True
    else:
        ret=ret+'\n'+'No Jitter detected'
    ret=ret+'\n peak width: {:.2f} ns'.format(peaks_width)

ret=ret+'\npeak loc at {:.2f} ns'.format(peak_max)


ret=ret+'\ntotal counts in hist: {}'.format(sum(hist))
print ret

pharp.StopMeas()
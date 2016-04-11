import msvcrt
import time


auto_corr_size= 100
auto_corr = np.zeros(auto_corr_size, dtype=np.int)
flen=0
blen=200000
ii=0
while 1:
    ii+=1
    t0=time.time()
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
        break
    a,b,c = qutau.get_last_timestamps()

    aa=np.array(a[0:blen])
    bb=np.array(b[0:blen])[aa>0]
    x = 2*bb[bb<2]-1
    flen+= len(x)
    if ii%1000==0:
        print auto_corr[0:20]
        print 1./np.sqrt(ii*len(bb))
    print x[1]
    break
    for j in np.arange(1,auto_corr_size):
        #print np.corrcoef(np.array([x[0:len(x)-j], x[j:len(x)]]))
        #auto_corr_j = np.corrcoef(np.array([x[0:len(x)-j], x[j:len(x)]]))
        auto_corr[j] += np.sum(x[0:len(x)-j]*x[j:len(x)])
    t1=time.time()
    if t1-t0 < 0.2:
        #print 0.2-(t1-t0)
        time.sleep(0.2-(t1-t0))

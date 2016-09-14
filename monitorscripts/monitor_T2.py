import qt
import time
import msvcrt

mm = qt.instruments['kei2000']


def get_temperature():
   
    R = kei2000.get_readlastval()
    
    t = (R-100)/0.385

    return R,t

t0 = time.time()
data = qt.Data(name='temp_monitor')
data.add_coordinate('time')
data.add_coordinate('Resistance')
data.add_coordinate('temperature')
data.create_file()

plt = qt.Plot2D(data, 'ro', name='Temperature', coorddim=0,
        valdim=1, clear=True)
plt.add(data, 'bo', coorddim=0, valdim=2, right=True)
plt.set_xlabel('time (h)')
plt.set_ylabel('T-sensor Resistance')
plt.set_y2label('T (K)')

print 'press q to quit'

while 1:
    if msvcrt.kbhit():
        kb_char=msvcrt.getch()
        if kb_char == "q":

            break

    R,t = get_temperature()
    data.add_data_point((time.time()-t0)/3600., R, t)

    qt.msleep(10)

if TH_260N.OpenDevice():
    TH_260N.start_T2_mode()
    TH_260N.set_Binning(0)
    print TH_260N.get_ResolutionPS()
else:
    raise(Exception('Picoquant instrument '+TH_260N.get_name()+ ' cannot be opened: Close the gui?'))

T2_READMAX = TH_260N.get_T2_READMAX()
TH_260N.StartMeas(int(100 * 1e3))
qt.msleep(3)
_length, _data = TH_260N.get_TTTR_Data()
if _length > 0:
    print _length
    if _length > T2_READMAX-100:
        logging.warning(': TTTR record length is maximum length, \
                         could indicate too low transfer rate resulting in buffer overflow.')
TH_260N.StopMeas()
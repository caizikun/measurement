"""
Driver for a virtual instrument to scan the entire diamond. 
This driver uses some specific pecularities of RT2 (specifically the coarse scanning stage) as well as the library openCV for python.
"""

from instrument import Instrument
import qt
import types
import numpy as np
import cv2
import instrument_helper
from analysis.lib.image_analysis import camera_tools as ct
from matplotlib import pyplot as plt
from analysis.lib.tools import toolbox as tb
from analysis.lib.fitting import common,fit
import msvcrt

class diamond_scanner(Instrument):
    """
    Uses image recognition techniques to do the following tasks: 
    a) Record locations on the ideal ebeam pattern of the system.
    b) Bring the diamond into focus.
    c) Perform 2D scans in a repetitive fashion (Simple method is done)
    d) TODO: Ideally finds/records NV locations.
    e) TODO: Even better performs a sequence of measurements on each NV found with some exclusion/inclusion criteria.
    f) This is probably one of those drivers that is never done.
    

    Additional functionaliry beyond core functions:
    TODO: add actual functionality to scan via coarse MOS
    TODO: add functionality to define a scan pattern (in terms of bit markers)
    TODO: add find bit marker
    TODO: store/compile information on each NV in a measurement folder
    TODO: make 'where_am_i' fucnction smarter such that it also works if no bit marker is in camera image
    """

    def __init__(self,name,mos,coarse_mos,remote_plug,**kw):
        logging.info(__name__ + ' : Initializing instrument Diamond scanner')
        Instrument.__init__(self, name)

        ### useful instruments
        self._adwin = qt.instruments['physical_adwin']
        self._mos = qt.instruments[mos]
        self._coarse_mos = qt.instruments[coarse_mos] 
        self._rem_plug = qt.instruments[remote_plug]
        self._aom = qt.instruments['GreenAOM']
        self._optimiz0r = qt.instruments['optimiz0r']
        self._scan2d = qt.instruments['scan2d']
        self._setup_controller = qt.instruments['setup_controller']

        ######## parameters
        ins_pars = { ### positioning
                    'x_pos'  :   {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'y_pos'  :   {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'last_x_pos'  :   {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':10}, ### used to check gross image misinterpretation
                    'last_y_pos'  :   {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':10}, ### used to check gross image misinterpretation
                    'sample_tilt_x': {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':0.1}, ### in nm per um
                    'sample_til_y' : {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':0.1}, ### in nm per um

                    'logged_distance_x' : {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'logged_distance_y' : {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':10},

                    ### anything ebeam pattern related
                    'bitm_pitch' :  {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':60},
                    'small_marker_pitch' :  {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':5},
                    'bitm_x_max' :  {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':5},
                    'bitm_y_max' :  {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':5},
                    'stripline_positions': {'type':types.Listtype,'flags':Instrument.FLAG_GETSET, 'val':[5,20]},
                    'stripline_width': {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':30},

                    ### image analysis:
                    'cam_path'  :   {'type':types.Stringtype,'flags':Instrument.FLAG_GETSET, 'val':''},
                    'cam_diameter_field_of_view' : {'type':types.Inttype,'flags':Instrument.FLAG_GETSET, 'val':30},
                    'cam_resolution' : {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':0.2},
                    'sample_rotation'  :   {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'l_spot_on_cam_x' :   {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'l_spot_on_cam_y' :   {'type':types.Floattype,'flags':Instrument.FLAG_GETSET, 'val':10},


        }

        instrument_helper.create_get_set(self,ins_pars)

        ### camera related 
        self.add_function('cam_where_am_i')
        self.add_function('cam_find_surface')
        self.add_function('cam_take_image')
        self.add_function('cam_load_latest_image')

        ### mos related
        self.add_fucntion('mos_go_to_bitmarker')
        self.add_function('mos_reset_fine_XY')

        ### data management 
        self.add_function('create_ebeam_pattern')
        self.add_function('update_ebeam_pattern')

        ### scanning + NV related
        self.add_function('generate_scanning_plan')
        self.add_function('execute_scanning_plan')
        self.add_function('save_NV_position_to_msmt_folder')
        self.add_function('find_nvs')

        self._ebeam_pattern = np.zeros((5,5)) ### dummy pattern

        ### priv variables
        self._last_where_am_i_succeeded = False
        self._scan_resolution = 10 ### 10 px per um
        self._scan_aom_power = 400e-6

    ######################################
    """ Public Methods DONE / BUG TEST """
    ######################################

    def cam_find_surface(self,do_plot = False):
        """
        copied and slightly adapted from estimate_z_surface.py
        """
        old_z = self._mos.get_z()
        old_aom_power =  self._aom.get_power()

        ### some parameters
        AOM_power = 100e-6
        z_range = 10
        z_range_fine = 1.5
        pts = 20
        self._aom.set_power(AOM_power)
        dat = np.zeros(pts)


        zs = np.linspace(old_z-z_range,old_z+z_range,pts)
        self._mos.set_z(zs[0])
        qt.msleep(1.5)

        #### loop over positions and count pixels ### find coarse surface position
        for ii,z in enumerate(zs):

            self._mos.set_z(z) ### change z
            qt.msleep(0.4) ### has to be longer than half a millisecond
            dat[ii] = phys_adwin.Get_Par(79) ### get the numberof white pixels in the camera image

        p_c = qt.Plot2D(name=name, clear=True)
        p_c.add(zs, dat, 'bO')
        #### create and save raw data
        d = qt.Data(name=name+'_estimate_z_surface')
        d.add_coordinate('relative focus (um)')
        d.add_value('number of white pixels')
        d.add_data_point(zs, dat)


        fine_zs = zs
        for i in range(2):
            z_min_coarse = fine_zs[np.argmin(dat)]

            fine_zs = np.linspace(z_min_coarse-z_range_fine,z_min_coarse+z_range_fine,int(pts/2.))
            dat = np.zeros(int(pts/2.))
            self._mos.set_z(fine_zs[0])
            qt.msleep(1.5)

            for ii,z in enumerate(fine_zs):
                self._mos.set_z(z) ### change z
                qt.msleep(0.4) ### has to be longer than half a millisecond
                dat[ii] = phys_adwin.Get_Par(79) ### get the numberof white pixels in the camera image

        self._mos.set_z(old_z)
        self._aom.set_power(old_aom_power)

        #### create and save raw data
        d.add_data_point(fine_zs, dat)


        #### fit parabola to data

        g_o = np.amin(dat) ### offset
        g_c = fine_zs[np.argmin(dat)] ### centre of the parabole
        g_A = abs((np.amax(dat)-np.amin(dat))/(fine_zs[np.argmin(dat)]-fine_zs[np.argmax(dat)]))
        p0,fitfunc,fitfunc_str = common.fit_parabole(g_o,g_A,g_c)

        fit_result = fit.fit1d(fine_zs,dat,None, p0 = p0, fitfunc = fitfunc,do_print = False, ret = True, fixed = [])

        x_fit = np.linspace(fine_zs[0],fine_zs[-1],200)
        #### plot data and 
        if do_plot:
            p_c = qt.Plot2D(name=name, clear=True)
            p_c.add(fine_zs, dat, 'bO')
            p_c.add(x_fit,fit_result['fitfunc'](x_fit),'r-')


        if fit_result['success']:
            self._mos.set_z(fit_result['params_dict']['c'])
            return True
        else:
            print "could not find the surface!!"
            return False


    def cam_where_am_i(self,show_current_pos = False,return_current_pos = False):
        """
        if success full:
            returns bitmarker position (bitx/bity)
        """
        suc = self.cam_find_surface()
        if not suc:
            self._last_where_am_i_succeeded = False
            print 'cannot find surface easily! TODO: Develope coarse surface search method'
            return

        self._aom.turn_off()
        self.cam_take_image()
        qt.msleep(1)
        img = ct.stamp_out_relevant_field_of_view(self.cam_load_image())
        img = ct.rotate_image(img,self.get_sample_rotation())

        self.filtered_laplacian = self._cam_apply_laplace_filter(img)

        self.im_with_keypoints,self.keypoints,self.laplace_8bit  = ct.find_marker_grid_via_blob_finder(filtered_laplacian,plot_histogram = False)

        self.grid_avg_slope,self.grid_avg_distance,self.grid_x0,self.grid_y0 = ct.estimate_grid_from_keypts(self.im_with_keypoints,self.keypoints,plot_fitted_lines = True)

        #### if successful we can update the sample angle!

        all_marker_pts = ct.get_grid_crossing_pts(self.grid_x0,self.grid_y0,self.grid_avg_slope,self.grid_avg_distance)
        filtered_img = ct.stamp_out_marker_grid_onto_im(laplace_8bit,all_marker_pts,1/self.get_cam_resolution(),show_images = False)

        bit_x,bit_y,suc = ct.find_bit_marker_in_image(filtered_img)
        if not suc:
            print 'no bit marker in image found'
            self._last_where_am_i_succeeded = False
            return x,y,False

        laserspot_x,laserspot_y = ct.distance_bitm_and_laserspot(bit_x,bit_y,l_spot_on_cam_x,l_spot_on_cam_y)

        binary_bit_marker = ct.zoom_in_on_bitmarker(img,bit_x,bit_y)
        bitmarker_array = np.flipud(np.reshape(ct.get_bit_marker_array(binary_bit_marker),(4,4)))
        bitx,bity  = ct.get_bitm_xy_from_array(bitmarker_array)

        self._last_where_am_i_succeeded = True

        self._current_ebeam_pattern_slice = ct.pattern_zoom_on_bitm(self._ebeam_pattern,bitx,bity,rel_size = 1.5,rel_shift_y = laserspot_x,rel_shift_x = laserspot_y),size=5,no_col_bar = True)
        if show_current_pos:
            ct.show_image(self._current_ebeam_pattern_slice)


        x,y = ct.find_current_ebeam_coordinates(self._ebeam_pattern,bitm_x,bitm_y,laserspot_x,laserspot_y,bitm_pitch = 60,correct_lift_off_problems = True)


        ##### DEBUG ME!!!!
        # self.set_latest_x(self.get_x_pos()),self.set_latest_y(self.get_y_pos())
        # self.set_x_pos(x),self.set_y_pos(y)

        # self.compare_latest_and_estimated_pos()
        if return_current_pos:
            return x,y,True


    def cam_load_image(self,filepath = None):

        if filepath == None:
            filepath = r'D:\measuring\Labview\CCDcamera\latest_image.dat'

        return np.loadtxt(filename,delimiter='\t',ndmin = 2)

    def create_ebeam_pattern(self,**kw):
        """
        striplines are assumed to be horizontal at the moment.
        If you want fancier striplines + bondpads then develop your own drawing skills.
        """

        self.set_small_marker_pitch(kw.pop('small_marker_pitch',5))
        self.set_bitm_x_max(kw.pop('bitm_x_max',36))
        self.set_bitm_y_max(kw.pop('bitm_y_max',15))
        self.set_bitm_pitch(kw.pop('bitm_bitm',60))
        self.set_stripline_width(kw.pop('stripline_width',30)) 
        self.set_stripline_positions(kw.pop('stripline_positions',[240+4,244+474])) #### position in the y direction

        self._ebeam_pattern = ct.generate_marker_pattern(small_marker_pitch = self.get_small_marker_pitch() ,bitm_x_max = self.get_bitm_x_max(),bitm_y_max = self.get_bitm_y_max(),bitm_pitch = self.get_bitm_pitch())
        self._ebeam_pattern = ct.add_striplines_to_img(self._ebeam_pattern,stripline_width = self.get_stripline_width(),stripline_centre = self.get_stripline_positions())

        return

    def mos_move_to_relative_pos(self,x,y,z):
        """     Moves fine piezos by a relative amount. Input coordinates are expressed in ebeam coordinates        """
        self._mos.move_to_xyz_pos(['x','y','z'],[self._mos.get_x()+x,self._mos.get_y()+y,self._mos.get_z()+z])

    def calculate_bitmarker_distance(self,x1,x2,y1,y2):
        return self.bitm_pitch*(x2-x1),self.bitm_pitch(y2-y1)

    def coord_rel_ebeam_to_fine_piezos(self,dx,dy):
        return coord_rel_camera_to_fine_piezos(coord_rel_ebeam_to_camera(dx,dy))

    def coord_rel_camera_to_coarse_piezos(self,dx,dy):
        return camera_to_coarse_piezos(coord_rel_ebeam_to_camera(dx,dy))

    def mos_reset_fine_XY(self):
        """moves to the central settings of the fine piezos"""
        self._mos.move_to_xyz_pos(['x','y'],[-45.2,51.02]) ## from lib/config/moss.py

    def turn_lights_off(self):
        """Turns camera light off"""
        self._rem_plug.turn_off('light_source')
    def turn_lights_on(self):
        """Turns camera light on"""
        self._rem_plug.turn_on('light_source')

    def generate_simple_scanning_plan(self,dx,dy,scan_depth = 3,scan_width = 50):
        """
        scans are defined in terms of a line on the ebeam pattern. Distances (dx,dy) are defined in um.
        The current position is assumed to be the start (minus nulling of the mos).
        The system acknowledges the sample tilt and compensates for it.

        Outputs a list of instructions that can then be fed into the function execute_scanning_plan.

        Instructions are basically dictionaries containing a single key (the action to be performed) and a list of parameters or more dictionaries with further parameters
        """
        
        self._todo_list = []

        dx_real,dy_real = self.coord_rel_ebeam_to_coarse_piezos(dx,dy) ### need to figure out effective movement of the steppers

        ##### cut the scan plan up into dx,dy per individual scan. We make this sample tilt dependent. No more than 1 um depth deviation per individual scan
        tilt_x,tilt_y = self.get_sample_tilt_x(),self.get_sample_tilt_y()


        segments_x,segments_y = np.floor(tilt_x*scan_width),np.floor(tilt_y*scan_width) ### round down. so effectively allow a tilt of 2 um.
        if segments_x == 0: segments_x = 1 ### no scans because of no tilt is not an option
        if segments_y == 0: segments_y = 1 ### no scans because of no tilt is not an option


        no_of_segments_per_scan_location = segments_x*segments_y

        total_no_of_scan_locations = np.ceiling(np.sqrt(dx**2+dy**2)/float(scan_width)) ### ceiling because more is better than too little.

        # self._todo_list = self._todo_list + [{'turn_lights_off':[]}] #XXXX

        for scan in range(total_no_of_scan_locations):

            self._todo_list = self._todo_list + [{'mos_reset_fine_XY':[]}] ### go to centre of scan range

            x0_fine = scan_width*(len(segments_x)-1)/2.
            y0_fine = scan_width*(len(segments_y)-1)/2.

            self._todo_list = self._todo_list + [{'mos_move_to_relative_pos':[x0_fine,y0_fine,0]}] ### move to centre of very first segment

            for s_x in range(segments_x):
                self._todo_list = self._todo_list + [{'mos_move_to_relative_pos':[(s_x != 0)*scan_width/(len(segments_x),0,0]}] ### move to centre of the current segment_x
                for s_y in range(segments_y):

                    self._todo_list = self._todo_list + [{'mos_move_to_relative_pos':[0,(s_y!=0)*scan_width/(len(segments_y),0]}] ### move to centre of the current segment_y
                    self._todo_list = self._todo_list + [{'cam_find_surface': []}] ### find z.
                    self._todo_list = self._todo_list + [{'mos_move_to_relative_pos':[0,0,-0.5]}]### want to only check what is under the surface ;)
                    
                    ### generate scan instructions
                    cur_x = self._mos.get_x()
                    cur_y = self._mos.get_y()
                    x0 , x1 = cur_x - scan_width/(2*len(segments_x)), cur_x + scan_width/(2*len(segments_x))
                    y0 , y1 = cur_y - scan_width/(2*len(segments_y)), cur_y + scan_width/(2*len(segments_y))
                    self._todo_list = self._todo_list + [{'do_2D_scans': ['scan_'+str(scan)+'segX_'+str(s_x)+'segY_'+str(s_y),x0,x1,y0,y1,range(scan_depth)]}]




            ### finally move on with the corase steppers
            total_no_of_scan_locations = float(total_no_of_scan_locations)
            self._todo_list = self._todo_list + [{'mos_coarse_move_rel': [dx_real/total_no_of_scan_locations,dy_real/total_no_of_scan_locations]}]

        return

    def do_2D_scans(self,name,x0,y0,x1,y1,dzs,pixeltime = 10.):
        """
        programs the setup to perform a series of green scans at a certain focal position (relative to the starting position)
        """
        cent_x,ceny = self._mos.get_x(),self._mos.get_y()
        z0 = self._mos.get_z()

        xpts = int(np.abs(x0-x1)/self._scan_resolution)+1
        ypts = int(np.abs(y0-y1)/self._scan_resolution)+1

        aom0 = self._aom.get_power()
        self._aom.set_power(self._scan_aom_power)

        self._scan2d.set_xstart(x0)
        self._scan2d.set_xstop(x1)
        self._scan2d.set_ystart(y0)
        self._scan2d.set_ystop(y1)
        self._scan2d.set_pixeltime(pixeltime)

        stop_scan = False

        for dz in dzs:
            self._mos.set_z(z0+dz)
            setup_controller.set_keyword(name+'dz_%s'%np.round(dz,2))

            self._scan2d.set_is_running(True)
            while(self._scan2d.get_is_running()):
                qt.msleep(0.1)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
                if stop_scan: self._scan2d.set_is_running(False); break
            qt.msleep(5)


        self._aom.set_power(aom0)   
        self._mos.set_x(cent_x),self._mos.set_y(cent_y)

        return True

    def execute_scanning_plan(self):
        """
        goes through self._todo_list and executes one instruction after the other.
        instructions are dictionaries with a single key that is assigned to a list of values.
        {'function_name' : [val1,val2,val3...]}
        we then execute the following command for each instruction self.function_name(val1,val2,val3...)
        Resets the todo_list when done.
        Inputs: None
        Outputs: None 
        """
        for instruction in self._todo_list:
            execstring = instruction.keys()[0]
            args = instruction[execstring]

            execstring = 'self.' + execstring
            args_string = '('
            for arg in args[:-1]:
                args_string = args_string+','
            args_string = args_string + args[-1]+')'

            exec(execstring+args_string)

        self._todo_list = []
    

    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value
    ###########################
    """ Public Methods TODO """
    ###########################



    def cam_take_image(self):
        """
        Currently no driver for the MatrixVision acquisition card. We trigger the labview program by setting a parameter in the adwin.
        TODO: Implement remote power plug driver.
        """
        # if self._rem_plug.get_is_on('light_source'):
        #   self._phys_adwin.Set_Par(80,1)
        # else:
        #   self._rem_plug.turn_on('light_source')
        #   qt.msleep(2)
        self._phys_adwin.Set_Par(80,1)



    def mos_go_to_bitmarker(self,bit_x,bit_y,iteration = 0):
        """
        TODO
        tries to find out where you are and then move towards the right bitmarker
        """

        ### TODOreset the fine piezos in XY

        x,y,suc = self.cam_where_am_i(return_current_pos = True)

        if not suc:
            print 'TODO: do something smart if no bitmarker is recognized in the image'

        ### calculate distance

        ### rotate into physical movement

        ### move in steps towards goal  

        ### check are we there yet? if yes: done; if no: redo!


    def compare_latest_and_current_pos(self):
        """
        This function evaluates whether the distance travelled makes sense
        TODO and what are the consequences if it does not.
        """

        x0,y0,x1,y1,dx,dy=[self.get_x_pos(),self.get_y_pos(),self.get_latest_x_pos(),self.get_latest_y_pos(),self.get_logged_distance_x(),self.get_logged_distance_y()]

        x0-x1 = dx2
        y0-y1 = dy2
        if abs(dx-dx2)/dx2*dx > 0.2 or abs(dy-dy2)/dy2*dy > 0.2:
            print "suspiciously high deviation in travelled distance! more local search recommended!"
        else:
            self.set_logged_distance_x(0)
            self.set_logged_distance_y(0)






    def generate_scanning_plan_bitm(self,list_of_bitm,x_rel_to_bitm,y_rel_to_bitm,scan_depth = 3,scan_width = 50):
        """
        very similar to generate_scanning_plan. However locations are defined in terms of numbers of bitmarkers.
        Will heavily rely on the function mos_go_to_bitmarker.
        TODO
        """
        self._todo_list = []
        return





    def find_NVs(self,timestamp):
        """analysis of past scans for nv finding"""
        pass

    def save_NV_position_to_msmt_folder(self,timestamp):
        """creates msmt folder and stores NV information in said msmt folder"""
        pass

    def coord_rel_ebeam_to_camera(self,dx,dy):
        """
        input are relative coordinates from current positions
        TODO bugcheck!
        """
        if self._last_where_am_i_succeeded:
            angle = self.get_sample_rotation()
            

            x_cam = np.cos(angle)*dx-np.sin(angle)*dy
            y_cam = np.sin(angle)*dx+np.cos(angle)*dy
            y_cam = -y_cam ## camera image is flipped along the vertical axis
            return x_cam,y_cam
        else:
            print "Location is unknown, can't conduct relative movements based on ebeam pattern"
            return 0,0 ### 0,0 indicates no relative movement
    def coord_rel_camera_to_fine_piezos(self,dx,dy):
        """
        physically knows what is up or down. heavy lifting is done by coord_ebeam_to_camera
        """
        pass

    def coord_rel_camera_to_coarse_piezos(self,dx,dy):
        """
        physically knows what is up or down. heavy lifting is done by coord_ebeam_to_camera
        """
        pass


    def ebeam_pattern_load(self,timestamp = None):
        """TODO loads_ebeam_patterns from file/timestamps"""
        pass

    def ebeam_pattern_save(self,timestamp = None):
        """TODO: stores np array along side other data in the latest msmt file"""
        pass
    


    #######################
    """ Private Methods """
    #######################

    def _cam_apply_laplace_filter(self,img):
        """ besides applying a filter based on derivatives this function also applies a phenomenological threhsold"""
        laplacian = cv2.Laplacian(img,cv2.CV_64F,ksize=21)
        laplacian = (laplacian-(np.amax(laplacian)+np.amin(laplacian))/2.) ## centre around 0
        laplacian = 2*laplacian/(np.amax(laplacian)-np.amin(laplacian)) ## normalize to interval of -1 to 1
        return ct.apply_brightness_filter(laplacian,-1.0,threshold_max= 0.2)
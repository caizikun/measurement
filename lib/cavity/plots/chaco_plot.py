# chaco plotting for use with cyclops
from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

# major lib imports
import sys
import time
from numpy import linspace, r_, meshgrid, sinc, zeros, exp

# Qt imports
from PyQt4 import QtGui, Qt, QtCore
#from enthought.qt import QtGui, Qt, QtCore

# enthought stuff
try:
    from enthought.enable.api import BaseTool, Window
    from enthought.traits.api import HasTraits, Instance, DelegatesTo, Delegate

    # chaco
    from enthought.chaco import default_colormaps
    from enthought.chaco.api import ArrayPlotData, ColorBar, HPlotContainer, \
        LinearMapper, Plot, PlotAxis
    from enthought.chaco.tools.api import PanTool, ZoomTool
    from enthought.chaco.tools.cursor_tool import CursorTool, BaseCursorTool
    from enthought.chaco.tools.image_inspector_tool import ImageInspectorTool, \
         ImageInspectorOverlay

except ImportError: # on my xubuntu system at least, these modules are not enthought.* submodules
    from enable.api import BaseTool, Window
    from traits.api import HasTraits, Instance, DelegatesTo, Delegate

    # chaco
    from chaco import default_colormaps
    from chaco.api import ArrayPlotData, ColorBar, HPlotContainer, \
        LinearMapper, Plot, PlotAxis
    from chaco.tools.api import PanTool, ZoomTool
    from chaco.tools.cursor_tool import CursorTool, BaseCursorTool
    from chaco.tools.image_inspector_tool import ImageInspectorTool, \
         ImageInspectorOverlay

### constants
DEFAULT_CMAP = 'jet'


### Some Helper classes, not meant for users;

class CrossHair(HasTraits):

    cursor = Instance(BaseCursorTool)
    cursor_pos = DelegatesTo('cursor', prefix='current_position')
    drag_state = DelegatesTo('cursor', prefix='_drag_state')

    # FIXME: implement dragging signal
    def __init__(self, plot, pos_signal, drag_signal=None):
        super(CrossHair, self).__init__()

        self._pos_signal = pos_signal
        self._drag_signal = drag_signal
        
        csr = CursorTool(plot,
                         drag_button='left',
                         color='white',
                         line_width=2.0,
                         marker_size=2.0)
        self.cursor = csr
        csr.current_position = 0.0, 0.0
        plot.overlays.append(csr)

        self.is_being_dragged = False

    def _cursor_pos_changed(self):
        # only emit if user drags, not for automated set
        if self.drag_state == 'dragging':
            self._pos_signal.emit(self.cursor_pos[0], self.cursor_pos[1])

    def _drag_state_changed(self):
        if self.drag_state == 'dragging':
            self.is_being_dragged = True
        else:
            self.is_being_dragged = False


class DataPicker(BaseTool):

    event_state = 'normal'

    def __init__(self, plot, signal):
        super(DataPicker, self).__init__(plot)
        self._signal = signal
    
    def normal_mouse_move(self, event):
         pos = self.component.map_data((event.x, event.y))
         self._signal.emit(pos[0], pos[1])

### The Available plots;

class BasePlot(QtGui.QWidget):

    crosshair_moved = QtCore.pyqtSignal(float, float)
    crosshair_dragged = QtCore.pyqtSignal(bool)
    mouse_moved = QtCore.pyqtSignal(float, float)
    
    def __init__(self, parent, **kw):
        QtGui.QWidget.__init__(self, parent)

        # TODO: kw processing - call enable-functions depending on kws

        
        self.plot = None
        self.data = None
        
        #self.enable_win = self._create_window(**kw)
        self._create_axes()
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        #layout.addWidget(self.enable_win.control)
        self.setLayout(layout)
        self.show()

    def clear(self):
        for p in self.plot.plots:
            self.plot.delplot(p)

    def enable_crosshair(self, name):
        self.crosshair = CrossHair(self.plot.plots[name][0],
                                   self.crosshair_moved)
        # self.crosshair_moved.connect(self._print_pos)

    def enable_data_picker(self):
        self.plot.tools.append(DataPicker(self.plot, self.mouse_moved))
        # self.mouse_moved.connect(self._print_pos)
        
    def enable_panning(self):
        self.plot.tools.append(PanTool(self.plot, constrain_key="shift"))
    
    def enable_zooming(self):
        zoom = ZoomTool(component=self.plot, tool_mode='box', always_on=False)
        self.plot.overlays.append(zoom)
        
    def set_crosshair_position(self, position):
        if hasattr(self, 'crosshair'):
            self.crosshair.cursor.current_position = position

    def set_data(self, data):
        pass

    def _create_axes(self):
        self.left_axis = PlotAxis(self.plot,
                                  orientation='left',
                                  title='x')
        self.bottom_axis = PlotAxis(self.plot,
                                    orientation='bottom',
                                    title='y')
        #self.plot.overlays.append(self.left_axis)
        #self.plot.overlays.append(self.bottom_axis)
        
    def _create_window(self, **kw):
        pass

    # a function for debugging. not used in practice.
    def _print_pos(self, x, y):
        print x, y

class ColorPlot(BasePlot): 
    def __init__(self, parent, **kw):

        self._cbar_axis_format = kw.pop('cbar_axis_format', '')
        self._plotname = kw.pop('plotname', 'color_plot')
        
        # TODO: enables via kws
        
        BasePlot.__init__(self, parent, **kw)

        # defaults from cyclops config
        #import cyclops
        #if cyclops.config.has_key('plot_colors'):
        #    cmap = cyclops.config['plot_colors'].get('colorplot_cmap', 
        #        DEFAULT_CMAP)
        #    self.set_colormap_by_name(cmap)


    ### public methods

    def enable_colorbar_panning(self):
        self._colorbar.tools.append(PanTool(self._colorbar,
                                            constrain_direction='y',
                                            constrain=True))

    def enable_colorbar_zooming(self):
        zoom_overlay = ZoomTool(self._colorbar, axis='index', tool_mode='range',
                                always_on=True, drag_button='right')
        self._colorbar.overlays.append(zoom_overlay)
        
    def set_colormap_by_name(self, colormap):
        if hasattr(default_colormaps, colormap):
            self._colormap = getattr(default_colormaps, colormap)
            value_range = self.plot.color_mapper.range
            self.plot.color_mapper = self._colormap(value_range)
            self._colorbar.color_mapper = self._colormap(value_range)
            self.container.request_redraw()
            
    def set_colormap(self, colormap):
        self._colormap = colormap
        value_range = self.plot.color_mapper.range
        self.plot.color_mapper = self._colormap(value_range)
        self._container.request_redraw()

    def set_data(self, x, y, z, **kw):
        #self.data.set_data('2d_data', z)
        #if self.plot.plots.has_key(self._plotname):
        #    self.plot.delplot(self._plotname)

        # determine correct bounds
        xstep = (x.max() - x.min())/(len(x)-1)
        ystep = (y.max() - y.min())/(len(y)-1)
        x0, x1 = x.min() - xstep/2, x.max() + xstep/2
        y0, y1 = y.min() - ystep/2, y.max() + ystep/2
        
        self.plot.img_plot('2d_data',
                           name = self._plotname,
                           xbounds = (x0, x1),
                           ybounds = (y0, y1),
                           colormap = self._colormap, **kw)[0]

        # if we have a cursor, need to redraw
        if hasattr(self, 'crosshair'):
            #pos = self.crosshair.cursor_pos
            self.enable_crosshair('color_plot')
            #self.crosshair.cursor_pos = pos
        

    ### private methods

    def _create_window(self, **kw):
        self._colormap = default_colormaps.jet       
        
        self.data = ArrayPlotData()
        self.plot = Plot(self.data)

        x = linspace(-10, 10, 101)
        y = linspace(-10, 10, 101)
        z = zeros((101,101))

        self.set_data(x, y, z, **kw)
        
        # self.set_data(x,y,z)        
        self._create_colorbar()
        self.container = HPlotContainer(use_backbuffer=True)
        self.container.add(self.plot)
        self.container.add(self._colorbar)
        
        return Window(self, -1, component=self.container)

    def _create_colorbar(self):
        cmap = self.plot.color_mapper
        self._colorbar = ColorBar(index_mapper=LinearMapper(range=cmap.range),
                                  color_mapper=cmap,
                                  orientation='v',
                                  resizable='v',
                                  width=30,
                                  padding=30,
                                  axis_visible=False)
        self._colorbar.plot = self.plot
        self._colorbar.padding_top = self.plot.padding_top
        self._colorbar.padding_bottom = self.plot.padding_bottom

        # create an axis as well
        kwargs = {'orientation' : 'left',
                  'title' : 'z'}
        if self._cbar_axis_format != '' :
            f = lambda val: ('%s' % self._cbar_axis_format) % val
            kwargs['tick_label_formatter'] = f
        
        self.colorbar_axis = PlotAxis(self._colorbar, **kwargs)
        self._colorbar.underlays.append(self.colorbar_axis)
    

class LinePlot(BasePlot):
    def __init__(self, parent, **kw):
        BasePlot.__init__(self, parent, **kw)

    def add_y(self, y, yname, **kw):
        self.data.set_data(yname, y)
        if self.plot.plots.has_key(yname):
            self.plot.delplot(yname)
        self.plot.plot(('x', yname), name=yname, **kw)
        self.plot.request_redraw()
        
    def set_x(self, x):
        self.data.set_data('x', x)

    def set_y(self, yname, y):
       if self.plot.plots.has_key(yname):
            self.plot.delplot(yname)
       self.data.set_data(yname, y)
       self.plot.plot(('x', yname), name=yname, **kw)
        
    def _create_window(self):
        self.data = ArrayPlotData()
        self.plot = Plot(self.data)

        return Window(self, -1, component=self.plot)

class TracePlot(BasePlot):
    def __init__(self, parent, **kw):

        self._type = kw.pop('type', 'scatter')
        self.nr_of_points = kw.pop('nr_of_points', 0)
        # TODO: more options
        
        BasePlot.__init__(self, parent, **kw)

    def add_point(self, x, y):
        self._x.append(x)
        self._y.append(y)
        self._set_data()

    def set_nr_of_points(self, n):
        self.nr_of_points = n
        self._set_data()

    def reset(self):
        self._x = []
        self._y = []
        self._set_data()

    def _set_data(self):
        if self.nr_of_points > 0:
            while len(self._x) > self.nr_of_points:
                self._x = self._x[1:]
                self._y = self._y[1:]
        self.data.set_data('x', self._x)
        self.data.set_data('y', self._y)
        
    def _create_window(self, **kw):
        self.data = ArrayPlotData()
        self.plot = Plot(self.data)

        self._x = []
        self._y = []
        self.data.set_data('x', self._x)
        self.data.set_data('y', self._y)

        self.plot.plot(('x', 'y'),
                       type = self._type,
                       name = 'trace')

        return Window(self, -1, component=self.plot)

class TimeTracePlot(TracePlot):
    def __init__(self, parent, **kw):
        
        self.display_time = kw.pop('display_time', 0)
        # self.memory_time = kw.pop('memory_time', 120)
        
        TracePlot.__init__(self, parent, **kw)

        self.bottom_axis.title = 'time [s]'
        self._zero = time.time()

    def add_point(self, y):
        x = time.time() - self._zero
        self._x.append(x)
        self._y.append(y)
        self._set_data()

    def reset(self):
        TracePlot.reset(self)
        self._zero = time.time()

    def set_display_time(self, t):
        self.display_time = t

    def _set_data(self):
        if self.display_time > 0:
            while self._x[-1] - self._x[0] > self.display_time:
                self._x = self._x[1:]
                self._y = self._y[1:]
        
        self.data.set_data('x', self._x)
        self.data.set_data('y', self._y)
             

if __name__ == '__main__':
    _app = QtGui.QApplication.instance()
    if _app is None:
        _app = QtGui.QApplication(sys.argv)

    main_window = QtGui.QWidget(size=QtCore.QSize(500,500))

    layout = QtGui.QVBoxLayout()
    layout.setMargin(0)

    # Example for a color plot
    '''
    plot = ColorPlot(main_window)
    print plot
    print type (plot)
    print dir(plot)
    xs = linspace(-10, 10, 51)
    ys = linspace(-10, 10, 51)
    x, y = meshgrid(xs,ys)
    z = 1e6*exp(-(x**2+y**2)/100)
    plot.set_data(xs, ys, z)

    
    plot.enable_colorbar_panning()
    plot.enable_colorbar_zooming()
    plot.colorbar_axis.title='counts [Hz]'
    plot.enable_crosshair('color_plot')
    '''

    # Example for a line plot
    #plot = LinePlot(main_window)
    #x = linspace(-3,3,101)
    #y = exp(-x**2)
    #plot.set_x(x)
    #plot.add_y(y, 'exp', name='exp')
    #plot.add_y(y/2, 'exp2', name='exp2', type='scatter', color='red') 


    # Example for a trace plot
    #plot = TimeTracePlot(main_window)
    
    # add plot to window
    layout.addWidget(plot)
    main_window.setLayout(layout)
    main_window.show()
    
    # general plot options
    #plot.enable_zooming()
    #plot.enable_panning()

    #plot.enable_data_picker()
    
    _app.exec_()
    



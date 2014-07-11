#/*##########################################################################
#
# The PyMca X-Ray Fluorescence Toolkit
#
# Copyright (c) 2004-2014 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
__author__ = "V.A. Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__doc__ = """
This module can be used for plugin testing purposes as well as for doing
the bookkeeping of actual plot windows. 

Functions to be implemented by an actual plotter can be found in the
abstract class PlotBackend.

"""
import sys
import numpy
from . import PlotBase
from .PlotBase import PlotBackend

DEBUG = 0
if DEBUG:
    PlotBase.DEBUG = True

# should the color handling belong to the PlotBase class?
colordict = {}
colordict['b'] = colordict['blue']   = '#0000ff'
colordict['r'] = colordict['red']    = '#ff0000'
colordict['g'] = colordict['green']  = '#00ff00'
colordict['k'] = colordict['black']  = '#000000'
colordict['white']  = '#ffffff'
colordict['pink']   = '#ff66ff'
colordict['brown']  = '#a52a2a'
colordict['orange'] = '#ff9900'
colordict['violet'] = '#6600ff'
colordict['gray'] = colordict['grey']   = '#a0a0a4'
#colordict['darkGray'] = colordict['darkGrey']   = '#808080'
#colordict['lightGray'] = colordict['lightGrey']   = '#c0c0c0'
colordict['y'] = colordict['yellow'] = '#ffff00'
colordict['m'] = colordict['magenta'] = '#ff00ff'
colordict['c'] = colordict['cyan'] = '#00ffff'
colordict['darkBlue'] = '#000080'
colordict['darkRed'] = '#800000'
colordict['darkGreen'] = '#008000'
colordict['darkBrown'] = '#660000' 
colordict['darkCyan'] = '#008080'
colordict['darkYellow'] = '#808000'
colordict['darkMagenta'] = '#800080'
colorlist  = [colordict['black'],
              colordict['blue'],
              colordict['red'],
              colordict['green'],
              colordict['pink'],
              colordict['yellow'],
              colordict['brown'],
              colordict['cyan'],
              colordict['magenta'],
              colordict['orange'],
              colordict['violet'],
              #colordict['bluegreen'],
              colordict['grey'],
              colordict['darkBlue'],
              colordict['darkRed'],
              colordict['darkGreen'],
              colordict['darkCyan'],
              colordict['darkMagenta'],
              colordict['darkYellow'],
              colordict['darkBrown']]

#PyQtGraph symbols ['o', 's', 't', 'd', '+', 'x']
#
#Matplotlib symbols:
#"." 	point
#"," 	pixel
#"o" 	circle
#"v" 	triangle_down
#"^" 	triangle_up
#"<" 	triangle_left
#">" 	triangle_right
#"1" 	tri_down
#"2" 	tri_up
#"3" 	tri_left
#"4" 	tri_right
#"8" 	octagon
#"s" 	square
#"p" 	pentagon
#"*" 	star
#"h" 	hexagon1
#"H" 	hexagon2
#"+" 	plus
#"x" 	x
#"D" 	diamond
#"d" 	thin_diamond
#"|" 	vline
#"_" 	hline
#"None" 	nothing
#None 	nothing
#" " 	nothing
#"" 	nothing
#

class Plot(PlotBase.PlotBase):
    PLUGINS_DIR = None

    colorList = colorlist
    colorDict = colordict

    def __init__(self, parent=None, backend=None, callback=None):
        self._parent = parent
        if backend is None:
            # an empty backend for testing purposes
            if "matplotlib" in sys.modules:
                from .backends.MatplotlibBackend import MatplotlibBackend as backend
                self._plot = backend(parent)
            else:
                self._plot = PlotBackend.PlotBackend(parent)
        else:
            self._plot = backend(parent)
            self._default = False
        super(Plot, self).__init__()
        widget = self._plot.getWidgetHandle()
        if widget is None:
            self.widget_ = self._plot
        else:
            self.widget_ = widget

        self.setCallback(callback)

        self.setLimits = self._plot.setLimits

        # curve handling
        self._curveList = []
        self._curveDict = {}
        self._activeCurve = None
        self._hiddenCurves = []

        #image handling
        self._imageList = []
        self._imageDict = {}
        self._activeImage = None

        # marker handling
        self._markerList = []
        self._markerDict = {}

        # item handling
        self._itemList = []
        self._itemDict = {}
        
        # colors and line types
        self._colorList = colorlist
        self._styleList = ['-', '--', '-.', ':']
        self._nColors   = len(colorlist)
        self._nStyles   = len(self._styleList)

        self._colorIndex = 0
        self._styleIndex = 0
        self._activeCurveColor = "#000000"

        # default properties
        self._logY = False
        self._logX = False
        
        self.setDefaultPlotPoints(False)
        self.setDefaultPlotLines(True)

        # zoom handling (should we take care of it?)
        self.enableZoom = self.setZoomModeEnabled
        self.setZoomModeEnabled(True)

    def enableActiveCurveHandling(self, flag=True):
        activeCurve = None
        if not flag:
            if self.isActiveCurveHandlingEnabled():
                activeCurve = self.getActiveCurve()
            self._activeCurveHandling = False
        else:
            self._activeCurveHandling = True
        self._plot.enableActiveCurveHandling(self._activeCurveHandling)
        if activeCurve is not None:
            self.addCurve(activeCurve[0],
                          activeCurve[1],
                          legend=activeCurve[2],
                          info=activeCurve[3])

    def isZoomModeEnabled(self):
        return self._plot.isZoomModeEnabled()

    def isDrawModeEnabled(self):
        return self._plot.isDrawModeEnabled()

    def getWidgetHandle(self):
        return self.widget_

    def setCallback(self, callbackFunction):
        if callbackFunction is None:
            self._plot.setCallback(self.graphCallback)
        else:
            self._plot.setCallback(callbackFunction)

    def graphCallback(self, ddict=None):
        """
        This callback is foing to receive all the events from the plot.
        Those events will consist on a dictionnary and among the dictionnary
        keys the key 'event' is mandatory to describe the type of event.
        This default implementation only handles setting the active curve.
        """

        if ddict is None:
            ddict = {}
        if DEBUG:
            print("Received dict keys = ", ddict.keys())
            print(ddict)
        if ddict['event'] in ["legendClicked", "curveClicked"]:
            if ddict['button'] == "left":
                self.setActiveCurve(ddict['label'])
    
    def setDefaultPlotPoints(self, flag):
        if flag:
            self._plotPoints = True
        else:
            self._plotPoints = False
        for key in self._curveList:
            if 'plot_symbol' in self._curveDict[key][3]:
                del self._curveDict[key][3]['plot_symbol']
        if len(self._curveList):
            self._update()

    def setDefaultPlotLines(self, flag):
        if flag:
            self._plotLines = True
        else:
            self._plotLines = False
        if len(self._curveList):
            self._update()

    def _getColorAndStyle(self):
        self._lastColorIndex = self._colorIndex
        self._lastStyleIndex = self._styleIndex
        if self._colorIndex >= self._nColors:
            self._colorIndex = 0
            self._styleIndex += 1
            if self._styleIndex >= self._nStyles:
                self._styleIndex = 0            
        color = self._colorList[self._colorIndex]
        style = self._styleList[self._styleIndex]
        if color == self._activeCurveColor:
            self._colorIndex += 1
            if self._colorIndex >= self._nColors:
                self._colorIndex = 0
                self._styleIndex += 1
                if self._styleIndex >= self._nStyles:
                    self._styleIndex = 0
            color = self._colorList[self._colorIndex]
            style = self._styleList[self._styleIndex]
        self._colorIndex += 1
        return color, style

    def setZoomModeEnabled(self, flag=True):
        self._plot.setZoomModeEnabled(flag)

    def setDrawModeEnabled(self, flag=True, shape="polygon", label=None, **kw):
        """
        Zoom and drawing are not compatible
        :param flag: Enable drawing mode disabling zoom and picking mode
        :type flag: boolean, default True
        :param shape: Type of item to be drawn
        :type shape: string, default polygon
        """
        self._plot.setDrawModeEnabled(flag=flag, shape=shape, label=label, **kw)

    def addItem(self, xdata, ydata, legend=None, info=None,
                replot=True, replace=False,
                shape="polygon", **kw):
        #expected to receive the same parameters as the signal
        if legend is None:
            key = "Unnamed Item 1.1"
        else:
            key = str(legend)
        if info is None:
            info = {}
        item = self._plot.addItem(xdata, ydata,
                                  legend=legend,
                                  info=info,
                                  shape=shape,
                                  **kw)
        info['plot_handle'] = item
        parameters = kw
        label = kw.get('label', legend)
        parameters['shape'] = shape
        parameters['label'] = label

        if legend in self._itemList:
            idx = self._itemList.index(legend)
            del self._itemList[idx]
        self._itemList.append(legend)
        self._itemDict[legend] = { 'x':xdata,
                                   'y':ydata,
                                   'legend':legend,
                                   'info':info,
                                   'parameters':parameters}
        return legend

    def removeItem(self, legend, replot=True):
        if legend is None:
            return
        if legend in self._itemList:
            idx = self._itemList.index(legend)
            del self._itemList[idx]
        if legend in self._itemDict:
            handle = self._itemDict[legend]['info'].get('plot_handle', None)
            del self._itemDict[legend]
            if handle is not None:
                self._plot.removeItem(handle, replot=replot)

    def getDrawMode(self):
        """
        Return a dictionnary (or None) with the parameters passed when setting
        the draw mode.
        :key shape: The shape being drawn
        :key label: Associated text (or None)
        and any other info
        """
        return self._plot.getDrawMode()

    def addCurve(self, x, y, legend=None, info=None, replace=False,
                 replot=True, **kw):
        """
        Add the 1D curve given by x an y to the graph.
        :param x: The data corresponding to the x axis
        :type x: list or numpy.ndarray
        :param y: The data corresponding to the y axis
        :type y: list or numpy.ndarray
        :param legend: The legend to be associated to the curve
        :type legend: string or None
        :param info: Dictionary of information associated to the curve
        :type info: dict or None
        :param replace: Flag to indicate if already existing curves are to be deleted
        :type replace: boolean default False
        :param replot: Flag to indicate plot is to be immediately updated
        :type replot: boolean default True
        """
        if legend is None:
            key = "Unnamed curve 1.1"
        else:
            key = str(legend)
        if info is None:
            info = {}
        xlabel = info.get('xlabel', 'X')
        ylabel = info.get('ylabel', 'Y')
        if 'xlabel' in kw:
            info['xlabel'] = kw['xlabel']
        if 'ylabel' in kw:
            info['ylabel'] = kw['ylabel']
        info['xlabel'] = str(xlabel)
        info['ylabel'] = str(ylabel)
        yaxis = info.get('yaxis', 'left')
        yaxis = kw.get('yaxis', yaxis)
        info['plot_yaxis'] = yaxis

        if replace:
            self._curveList = []
            self._curveDict = {}
            self._colorIndex = 0
            self._styleIndex = 0
            self._plot.clearCurves()

        symbol = None
        color = None
        line_style = None
        if key in self._curveList:
            idx = self._curveList.index(key)
            self._curveList[idx] = key
            handle = self._curveDict[key][3].get('plot_handle', None)
            if handle is not None:
                # this can give errors if it is not present in the plot
                self._plot.removeCurve(key, replot=False)
                symbol = self._curveDict[key][3].get('plot_symbol', symbol)
                color = self._curveDict[key][3].get('plot_color', color)
                line_style = self._curveDict[key][3].get('plot_line_style',
                                                    line_style)
        else:
            self._curveList.append(key)
        #print("TODO: Here we can add properties to the info dictionnary")
        #print("For instance, color, symbol, style and width if not present")
        #print("They could come in **kw")
        #print("The actual plotting stuff should only take care of handling")
        #print("logarithmic filtering if needed")
        # deal with the fill
        fill = info.get("plot_fill", False)
        fill = kw.get("fill", fill)
        info["plot_fill"] = fill

        # deal with the symbol
        symbol = info.get("plot_symbol", symbol)
        symbol = kw.get("symbol", symbol)
        if self._plotPoints and (symbol is None):
            symbol = 'o'
        elif symbol == "":
            #symbol = None
            pass
        info["plot_symbol"] = symbol
        color = info.get("plot_color", color)
        color = kw.get("color", color)

        line_style = info.get("plot_line_style", None)
        line_style = kw.get("line_style", line_style)

        if self._plotLines and (line_style is None):
            line_style = '-'
        elif line_style is None:
            line_style = ' '

        if (color is None) and (line_style is None):
            color, line_style = self._getColorAndStyle()
        elif line_style is None:
            dummy, line_style = self._getColorAndStyle()
        elif color is None:
            color, dummy = self._getColorAndStyle()
        #print("Legend = ", legend, "color = ", color, "style = ", line_style)
        info["plot_color"] = color
        info["plot_line_style"] = line_style
        info.get('plot_yaxis', 'left')

        if self.isXAxisLogarithmic() or self.isYAxisLogarithmic():
            xplot, yplot = self.logFilterData(x, y)
        else:
            xplot, yplot = x, y
        if len(xplot):
            curveHandle = self._plot.addCurve(xplot, yplot, key, info,
                                              replot=False, replace=replace)
            info['plot_handle'] = curveHandle
        else:
            info['plot_handle'] = key
        self._curveDict[key] = [x, y, key, info]

        if len(self._curveList) == 1:
            if self.isActiveCurveHandlingEnabled():
                self.setActiveCurve(key)

        if self.isCurveHidden(key):
            self._plot.removeCurve(key, replot=False)
        if replot:
            self.resetZoom()
            #self.replot()
        return legend

    def addImage(self, data, legend=None, info=None,
                 replace=True, replot=True,
                 xScale=None, yScale=None, z=0,
                 selectable=False, draggable=False,
                 colormap=None, **kw):
        """
        :param data: (nrows, ncolumns) data or (nrows, ncolumns, RGBA) ubyte array 
        :type data: numpy.ndarray
        :param legend: The legend to be associated to the curve
        :type legend: string or None
        :param info: Dictionary of information associated to the image
        :type info: dict or None
        :param replace: Flag to indicate if already existing images are to be deleted
        :type replace: boolean default True
        :param replot: Flag to indicate plot is to be immediately updated
        :type replot: boolean default True
        :param xScale: Two floats defining the x scale
        :type xScale: list or numpy.ndarray
        :param yScale: Two floats defining the y scale
        :type yScale: list or numpy.ndarray
        :param z: level at which the image is to be located (to allow overlays).
        :type z: A number bigger than or equal to zero (default)
        :param selectable: Flag to indicate if the image can be selected
        :type selectable: boolean, default False
        :param draggable: Flag to indicate if the image can be moved
        :type draggable: boolean, default False
        :param colormap: Dictionary describing the colormap to use (or None)
        :type colormap: Dictionnary or None (default). Ignored if data is RGB(A)
        :returns: The legend/handle used by the backend to univocally access it.
        """
        if legend is None:
            key = "Unnamed Image 1.1"
        else:
            key = str(legend)
        if info is None:
            info = {}
        xlabel = info.get('xlabel', 'Column')
        ylabel = info.get('ylabel', 'Row')
        if 'xlabel' in kw:
            info['xlabel'] = kw['xlabel']
        if 'ylabel' in kw:
            info['ylabel'] = kw['ylabel']
        info['xlabel'] = str(xlabel)
        info['ylabel'] = str(ylabel)

        if replace:
            self._imageList = []
            self._imageDict = {}
        if data is not None:
            imageHandle = self._plot.addImage(data, legend=key, info=info,
                                              replot=False, replace=replace,
                                              xScale=xScale, yScale=yScale,
                                              z=z,
                                              selectable=selectable,
                                              draggable=draggable,
                                              **kw)
            info['plot_handle'] = imageHandle
        else:
            info['plot_handle'] = key
        self._imageDict[key] = [data, key, info, xScale, yScale, z]
        if len(self._imageDict) == 1:
            self.setActiveImage(key)
        if replot:
            self.resetZoom()
            self.replot()
        return key

    def removeCurve(self, legend, replot=True):
        """
        Remove the curve associated to the supplied legend from the graph.
        The graph will be updated if replot is true.
        :param legend: The legend associated to the curve to be deleted
        :type legend: string or None
        :param replot: Flag to indicate plot is to be immediately updated
        :type replot: boolean default True        
        """
        if legend is None:
            return
        if legend in self._curveList:
            idx = self._curveList.index(legend)
            del self._curveList[idx]
        if legend in self._curveDict:
            handle = self._curveDict[legend][3].get('plot_handle', None)
            del self._curveDict[legend]
            if handle is not None:
                self._plot.removeCurve(handle, replot=replot)
        if not len(self._curveList):
            self._colorIndex = 0
            self._styleIndex = 0

    def removeImage(self, legend, replot=True):
        """
        Remove the image associated to the supplied legend from the graph.
        The graph will be updated if replot is true.
        :param legend: The legend associated to the image to be deleted
        :type legend: string or handle
        :param replot: Flag to indicate plot is to be immediately updated
        :type replot: boolean default True        
        """
        if legend is None:
            return
        if legend in self._imageList:
            idx = self._imageList.index(legend)
            del self._imageList[idx]
        if legend in self._imageDict:
            handle = self._imageDict[legend][2].get('plot_handle', None)
            del self._imageDict[legend]
            if handle is not None:
                self._plot.removeImage(handle, replot=replot)
        return

    def getActiveCurve(self, just_legend=False):
        """
        :param just_legend: Flag to specify the type of output required
        :type just_legend: boolean
        :return: legend of the active curve or list [x, y, legend, info]
        :rtype: string or list 
        Function to access the graph currently active curve.
        It returns None in case of not having an active curve.

        Default output has the form:
            xvalues, yvalues, legend, dict
            where dict is a dictionnary containing curve info.
            For the time being, only the plot labels associated to the
            curve are warranted to be present under the keys xlabel, ylabel.

        If just_legend is True:
            The legend of the active curve (or None) is returned.
        """
        if not self.isActiveCurveHandlingEnabled():
            return None
        if self._activeCurve not in self._curveDict:
            self._activeCurve = None
        if just_legend:
            return self._activeCurve
        if self._activeCurve is None:
            return []
        else:
            return self._curveDict[self._activeCurve] * 1

    def getActiveImage(self, just_legend=False):
        """
        :param just_legend: Flag to specify the type of output required
        :type just_legend: boolean
        :return: legend of the active image or list [data, legend, info, xScale, yScale, z]
        :rtype: string or list 
        Function to access the plot currently active image.
        It returns None in case of not having an active image.

        Default output has the form:
            data, legend, dict, xScale, yScale, z
            where dict is a dictionnary containing image info.
            For the time being, only the plot labels associated to the
            image are warranted to be present under the keys xlabel, ylabel.

        If just_legend is True:
            The legend of the active imagee (or None) is returned.
        """
        if self._activeImage not in self._imageDict:
            self._activeImage = None
        if just_legend:
            return self._activeImage
        if self._activeImage is None:
            return None
        else:
            return self._imageDict[self._activeImage] * 1

    def getAllCurves(self, just_legend=False):
        """
        :param just_legend: Flag to specify the type of output required
        :type just_legend: boolean
        :return: legend of the curves or list [[x, y, legend, info], ...]
        :rtype: list of strings or list of curves 

        It returns an empty list in case of not having any curve.
        If just_legend is False:
            It returns a list of the form:
                [[xvalues0, yvalues0, legend0, dict0],
                 [xvalues1, yvalues1, legend1, dict1],
                 [...],
                 [xvaluesn, yvaluesn, legendn, dictn]]
            or just an empty list.
        If just_legend is True:
            It returns a list of the form:
                [legend0, legend1, ..., legendn]
            or just an empty list.
        """
        output = []
        keys = list(self._curveDict.keys())
        for key in self._curveList:
            if key in keys:
                if self.isCurveHidden(key):
                    continue        
                if just_legend:
                    output.append(key)
                else:
                    output.append(self._curveDict[key])
        return output

    def getCurve(self, legend):
        """
        :param legend: legend assiciated to the curve
        :type legend: boolean
        :return: list [x, y, legend, info]
        :rtype: list 
        Function to access the graph currently active curve.
        It returns None in case of not having an active curve.

        Default output has the form:
            xvalues, yvalues, legend, dict
            where dict is a dictionnary containing curve info.
            For the time being, only the plot labels associated to the
            curve are warranted to be present under the keys xlabel, ylabel.
        """
        # let it raise en exception if not present
        return self._curveDict[legend] * 1


    def _getAllLimits(self):
        """
        Internal method to retrieve the limits based on the curves, not
        on the plot. It might be of use to reset the zoom when one of the
        X or Y axes is not set to autoscale.
        """
        keys = list(self._curveDict.keys())
        if not len(keys):
            return 0.0, 0.0, 100., 100.
        xmin = None
        ymin = None
        xmax = None
        ymax = None
        for key in keys:
            x = self._curveDict[key][0]
            y = self._curveDict[key][1]
            if xmin is None:
                xmin = x.min()
            else:
                xmin = min(xmin, x.min())
            if ymin is None:
                ymin = y.min()
            else:
                ymin = min(ymin, y.min())
            if xmax is None:
                xmax = x.max()
            else:
                xmax = max(xmax, x.max())
            if ymax is None:
                ymax = y.max()
            else:
                ymax = max(ymax, y.max())
        return xmin, ymin, xmax, ymax

    def saveGraph(self, filename, fileFormat='svg', dpi=None, **kw):
        """
        :param fileName: Destination
        :type fileName: String or StringIO or BytesIO
        :param fileFormat:  String specifying the format
        :type fileFormat: String (default 'svg')
        """
        return self._plot.saveGraph(filename,
                                    fileFormat=fileFormat,
                                    dpi=dpi,
                                    **kw)

    def setActiveCurve(self, legend, replot=True):
        """
        Funtion to request the plot window to set the curve with the specified legend
        as the active curve.
        :param legend: The legend associated to the curve
        :type legend: string
        """
        if not self.isActiveCurveHandlingEnabled():
            return
        oldActiveCurve = self.getActiveCurve(just_legend=True)
        key = str(legend)
        if key in self._curveDict.keys():
            self._activeCurve = key
        if self._activeCurve == oldActiveCurve:
            return self._activeCurve
        # this was giving troubles in the PyQtGraph binding
        #if self._activeCurve != oldActiveCurve:
        self._plot.setActiveCurve(self._activeCurve, replot=replot)
        return self._activeCurve

    def setActiveCurveColor(self, color="#000000"):
        if color is None:
            color = "black"
        if color in colordict:
            color = colordict[color]
        self._activeCurveColor = color
        self._plot.setActiveCurveColor(color)

    def setActiveImage(self, legend, replot=True):
        """
        Funtion to request the plot window to set the image with the specified legend
        as the active image.
        :param legend: The legend associated to the image
        :type legend: string
        """
        oldActiveImage = self.getActiveImage(just_legend=True)
        key = str(legend)
        if key in self._imageDict.keys():
            self._activeImage = key
        self._plot.setActiveImage(self._activeImage, replot=replot)
        return self._activeImage

    def invertYAxis(self, flag=True):
        self._plot.invertYAxis(flag)

    def isYAxisInverted(self):
        return self._plot.isYAxisInverted()

    def isYAxisLogarithmic(self):
        if self._logY:
            return True
        else:
            return False

    def isXAxisLogarithmic(self):
        if self._logX:
            return True
        else:
            return False
        
    def setYAxisLogarithmic(self, flag):
        if flag:
            if self._logY:
                if DEBUG:
                    print("y axis was already in log mode")
            else:
                self._logY = True
                if DEBUG:
                    print("y axis was in linear mode")
                self._plot.clearCurves()
                self._plot.setYAxisLogarithmic(self._logY)
                self._update()
        else:
            if self._logY:
                if DEBUG:
                    print("y axis was in log mode")
                self._logY = False
                self._plot.clearCurves()
                self._plot.setYAxisLogarithmic(self._logY)
                self._update()
            else:
                if DEBUG:
                    print("y axis was already linear mode")
        return

    def setXAxisLogarithmic(self, flag):
        if flag:
            if self._logX:
                if DEBUG:
                    print("x axis was already in log mode")
            else:
                self._logX = True
                if DEBUG:
                    print("x axis was in linear mode")
                self._plot.clearCurves()
                self._plot.setXAxisLogarithmic(self._logX)
                self._update()
        else:
            if self._logX:
                if DEBUG:
                    print("x axis was in log mode")
                self._logX = False
                self._plot.setXAxisLogarithmic(self._logX)
                self._update()
            else:
                if DEBUG:
                    print("x axis was already linear mode")
        return

    def logFilterData(self, x, y, xLog=None, yLog=None):
        if xLog is None:
            xLog = self._logX
        if yLog is None:
            yLog = self._logY

        if xLog and yLog:
            idx = numpy.nonzero((x > 0) & (y > 0))[0]
            x = numpy.take(x, idx)
            y = numpy.take(y, idx)
        elif yLog:
            idx = numpy.nonzero(y > 0)[0]
            x = numpy.take(x, idx)
            y = numpy.take(y, idx)
        elif xLog:
            idx = numpy.nonzero(x > 0)[0]
            x = numpy.take(x, idx)
            y = numpy.take(y, idx)
        return x, y

    def _update(self):
        if DEBUG:
            print("_update called")
        curveList = self.getAllCurves()
        activeCurve = self.getActiveCurve(just_legend=True)
        #self._plot.clearCurves()
        for curve in curveList:
            x, y, legend, info = curve[0:4]
            self.addCurve(x, y, legend, info=info,
                          replace=False, replot=False)
        if len(curveList):
            if activeCurve not in curveList:
                activeCurve = curveList[0][2]
            self.setActiveCurve(activeCurve)
        self.replot()

    def replot(self):
        if DEBUG:
            print("replot called")
        if self.isXAxisLogarithmic() or self.isYAxisLogarithmic():
            for image in self._imageDict.keys():
                self._plot.removeImage(image[1])
        if hasattr(self._plot, 'replot_'):
            self._plot.replot_()
        else:
            self._plot.replot()

    def clear(self):
        self._curveList = []
        self._curveDict = {}
        self._colorIndex = 0
        self._styleIndex = 0
        self._markerDict = {}
        self._imageList = []
        self._imageDict = {}        
        self._markerList = []
        self._plot.clear()
        self.replot()

    def clearCurves(self):
        self._curveList = []
        self._curveDict = {}
        self._colorIndex = 0
        self._styleIndex = 0
        self._plot.clearCurves()
        self.replot()

    def clearImages(self):
        """
        Clear all images from the plot. Not the curves or markers.
        """
        self._imageList = []
        self._imageDict = {}
        self._plot.clearImages()
        self.replot()
        return

    def resetZoom(self):
        self._plot.resetZoom()

    def setXAxisAutoScale(self, flag=True):
        self._plot.setXAxisAutoScale(flag)

    def setYAxisAutoScale(self, flag=True):
        self._plot.setYAxisAutoScale(flag)

    def isXAxisAutoScale(self):
        return self._plot.isXAxisAutoScale()

    def isYAxisAutoScale(self):
        return self._plot.isYAxisAutoScale()

    def getGraphTitle(self):
        return self._plot.getGraphTitle()

    def getGraphXLabel(self):
        return self._plot.getGraphXLabel()

    def getGraphYLabel(self):
        return self._plot.getGraphYLabel()

    def setGraphYLimits(self, ymin, ymax, replot=False):
        self._plot.setGraphYLimits(ymin, ymax)
        if replot:
            self.replot()

    def setGraphXLimits(self, xmin, xmax, replot=False):
        self._plot.setGraphXLimits(xmin, xmax)
        if replot:
            self.replot()

    def getGraphXLimits(self):
        """
        Get the graph X (bottom) limits.
        :return:  Minimum and maximum values of the X axis
        """
        if hasattr(self._plot, "getGraphXLimits"):
            xmin, xmax = self._plot.getGraphXLimits()
        else:
            xmin, ymin, xmax, ymax = self._getAllLimits()
        return xmin, xmax

    def getGraphYLimits(self):
        """
        Get the graph Y (left) limits.
        :return:  Minimum and maximum values of the X axis
        """
        if hasattr(self._plot, "getGraphYLimits"):
            ymin, ymax = self._plot.getGraphYLimits()
        else:
            xmin, ymin, xmax, ymax = self._getAllLimits()
        return ymin, ymax

    # Title and labels
    def setGraphTitle(self, title=""):
        self._plot.setGraphTitle(title)

    def setGraphXLabel(self, label="X"):
        self._plot.setGraphXLabel(label)

    def setGraphYLabel(self, label="Y"):
        self._plot.setGraphYLabel(label)
        
    # Marker handling
    def insertXMarker(self, x, legend=None,
                      label=None,
                      color=None,
                      selectable=False,
                      draggable=False,
                      **kw):
        """
        kw ->symbol
        """
        if DEBUG:
            print("Received label = %s" % label)
        if color is None:
            color = colordict['black']
        elif color in colordict:
            color = colordict[color]
        if legend is None:
            i = 0
            legend = "Unnamed X Marker %d" % i
            while legend in self._markerList:
                i += 1
                legend = "Unnamed X Marker %d" % i

        if legend in self._markerList:
            self.removeMarker(legend)
        marker = self._plot.insertXMarker(x, legend,
                                          label=label,
                                          color=color,
                                          selectable=selectable,
                                          draggable=draggable,
                                          **kw)
        self._markerList.append(legend)
        self._markerDict[legend] = kw
        self._markerDict[legend]['marker'] = marker
        return marker

    def insertYMarker(self, y,
                      legend=None,
                      label=None,
                      color=None,
                      selectable=False,
                      draggable=False,
                      **kw):
        """
        kw -> color, symbol
        """
        if color is None:
            color = colordict['black']
        elif color in colordict:
            color = colordict[color]
        if legend is None:
            i = 0
            legend = "Unnamed Y Marker %d" % i
            while legend in self._markerList:
                i += 1
                legend = "Unnamed Y Marker %d" % i
        if legend in self._markerList:
            self.clearMarker(legend)
        marker = self._plot.insertYMarker(y, legend,
                                          label=label,
                                          color=color,
                                          selectable=selectable,
                                          draggable=draggable,
                                          **kw)
        self._markerList.append(legend)
        self._markerDict[legend] = kw
        self._markerDict[legend]['marker'] = marker
        return marker

    def insertMarker(self, x, y, legend=None,
                     label=None,
                     color=None,
                     selectable=False,
                     draggable=False,
                     **kw):
        if color is None:
            color = colordict['black']
        elif color in colordict:
            color = colordict[color]
        if legend is None:
            i = 0
            legend = "Unnamed Marker %d" % i
            while legend in self._markerList:
                i += 1
                legend = "Unnamed Marker %d" % i

        if legend in self._markerList:
            self._plot.clearMarker(legend)
        marker = self._plot.insertMarker(x, y, legend,
                                          label=label,
                                          color=color,
                                          selectable=selectable,
                                          draggable=draggable,
                                          **kw)


        self._markerList.append(marker)
        self._markerDict[legend] = kw
        self._markerDict[legend]['marker'] = marker
        return marker

    def keepDataAspectRatio(self, flag=True):
        """
        :param flag:  True to respect data aspect ratio
        :type flag: Boolean, default True
        """
        self._plot.keepDataAspectRatio(flag=flag)

    def clearMarkers(self):
        self._markerDict = {}
        self._plot.clearMarkers()

        for marker in  self._markerList:
            self._plot.clearMarker(marker)

        self._markerList = []
        # self.replot()

    def removeMarker(self, marker):
        if marker in self._markerList:
            idx = self._markerList.index(marker)
            del self._markerList[idx]
            try:
                self._plot.removeMarker(self._markerDict[marker]['marker'])
                del self._markerDict[marker]
            except KeyError:
                if DEBUG:
                    print("Marker was not present %s"  %\
                          self._markerDict[marker]['marker'])

    def setMarkerFollowMouse(self, marker, boolean):
        raise NotImplemented("Not necessary?")
        if marker not in self._markerList:
            raise ValueError("Marker %s not defined" % marker)
        pass

    def enableMarkerMode(self, flag):
        raise NotImplemented("Not necessary?")
        pass

    def isMarkerModeEnabled(self, flag):
        raise NotImplemented("Not necessary?")
        pass

    def showGrid(self, flag=True):
        if DEBUG:
            print("Plot showGrid called")
        self._plot.showGrid(flag)

    # colormap related functions
    def getDefaultColormap(self):
        """
        Return the colormap that will be applied by the backend to an image
        if no colormap is applied to it.
        A colormap is a dictionnary with the keys:
        :type name: string
        :type normalization: string (linear, log)
        :type autoscale: boolean
        :type vmin: float, minimum value
        :type vmax: float, maximum value
        :type colors: integer (typically 256)
        """
        return self._plot.getDefaultColormap()
    
    def setDefaultColormap(self, colormap=None):
        """
        Sets the colormap that will be applied by the backend to an image
        if no colormap is applied to it.
        A colormap is a dictionnary with the keys:
        :type name: string
        :type normalization: string (linear, log)
        :type autoscale: boolean
        :type vmin: float, minimum value
        :type vmax: float, maximum value
        :type colors: integer (typically 256)

        If None is passed, the backend will reset to its default colormap.
        """
        self._plot.setDefaultColormap(colormap)

    def getSupportedColormaps(self):
        """
        Get a list of strings with the colormap names supported by the backend.
        The list should at least contain and start by:
        ['gray', 'reversed gray', 'temperature', 'red', 'green', 'blue']
        """
        return self._plot.getSupportedColormaps()

    def hideCurve(self, legend, flag=True, replot=True):
        if flag:
            self._plot.removeCurve(legend, replot=replot)
            if legend not in self._hiddenCurves:
                self._hiddenCurves.append(legend)
        else:
            while legend in self._hiddenCurves:
                idx = self._hiddenCurves.index(legend)
                del self._hiddenCurves[idx]
            if legend in self._curveDict:
                x, y, legend, info = self._curveDict[legend][0:4]
                self.addCurve(x, y, legend, info, replot=replot)

    def isCurveHidden(self, legend):
        return legend in self._hiddenCurves

def main():
    x = numpy.arange(100.)
    y = x * x
    plot = Plot()
    plot.addCurve(x, y, "dummy")
    plot.addCurve(x + 100, -x * x, "To set Active")
    print("Active curve = ", plot.getActiveCurve())
    print("X Limits = ", plot.getGraphXLimits())
    print("Y Limits = ", plot.getGraphYLimits())
    print("All curves = ", plot.getAllCurves())
    plot.removeCurve("dummy")
    plot.setActiveCurve("To set Active")
    print("All curves = ", plot.getAllCurves())
    plot.insertXMarker(50.)

if __name__ == "__main__":
    main()

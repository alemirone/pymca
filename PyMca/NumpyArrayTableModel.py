#/*##########################################################################
# Copyright (C) 2004-2009 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem for you.
#############################################################################*/
import numpy
from PyQt4 import QtCore, QtGui

class NumpyArrayTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, narray=None, fmt="%g", perspective=0):
        QtCore.QAbstractTableModel.__init__(self, parent)
        if narray is None:
            narray = numpy.array([])
        self._array  = narray
        self._format = fmt
        self._index  = 0
        self.assignDataFunction(perspective)

    def rowCount(self, parent=None):
        return self._rowCount(parent)

    def columnCount(self, parent=None):
        return self._columnCount(parent)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return self._data(index, role)

    def _rowCount1D(self, parent=None):
        return self._array.shape[0]

    def _columnCount1D(self, parent=None):
        return 1

    def _data1D(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = 0
                return QtCore.QVariant(self._format % self._array[row])
        return QtCore.QVariant()

    def _rowCount2D(self, parent=None):
        return self._array.shape[0]

    def _columnCount2D(self, parent=None):
        return self._array.shape[1]

    def _data2D(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(self._format % self._array[row, col])
        return QtCore.QVariant()

        
    def _rowCount3DIndex0(self, parent=None):
        return self._array.shape[1]

    def _columnCount3DIndex0(self, parent=None):
        return self._array.shape[2]            

    def _rowCount3DIndex1(self, parent=None):
        return self._array.shape[0]

    def _columnCount3DIndex1(self, parent=None):
        return self._array.shape[2]            

    def _rowCount3DIndex2(self, parent=None):
        return self._array.shape[0]

    def _columnCount3DIndex2(self, parent=None):
        return self._array.shape[1]            

    def _data3DIndex0(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(self._format % self._array[self._index,
                                                                  row,
                                                                  col])
        return QtCore.QVariant()

    def _data3DIndex1(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(self._format % self._array[row,
                                                                  self._index,
                                                                  col])
        return QtCore.QVariant()

    def _data3DIndex2(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(self._format % self._array[row,
                                                                  col,
                                                                  self._index])
        return QtCore.QVariant()

    def setArrayData(self, data, perspective=0):
        """
        setStackData(self, data, perspective=0)
        data is a 3D array
        dimension is the array dimension acting as index of images
        """
        self._array = data
        self.assignDataFunction(perspective)
        self._index = 0

    def assignDataFunction(self, dimension):
        shape = self._array.shape
        if len(shape) == 2:
            self._rowCount = self._rowCount2D
            self._columnCount = self._columnCount2D
            self._data = self._data2D
        elif len(shape) == 1:
            self._rowCount = self._rowCount1D
            self._columnCount = self._columnCount1D
            self._data = self._data1D
        else:
            if dimension == 1:
                self._rowCount = self._rowCount3DIndex1
                self._columnCount = self._columnCount3DIndex1
                self._data = self._data3DIndex1
            elif dimension == 2:
                self._rowCount = self._rowCount3DIndex2
                self._columnCount = self._columnCount3DIndex2
                self._data = self._data3DIndex1
            else:
                self._rowCount = self._rowCount3DIndex0
                self._columnCount = self._columnCount3DIndex0
                self._data = self._data3DIndex0
            self._dimension = dimension

    def setCurrentArrayIndex(self, index):
        """
        This method is ignored if the current array does not
        not a 3-dimensional array.
        """
        shape = self._array.shape
        if len(shape) != 3:
            return
        shape = self._array.shape[self._dimension]
        if (index < 0) or (index >= shape):
            raise ValueError, "Index must be an integer lower than %d" % shape
        self._index = index

    def setFormat(self, fmt):
        self._format = fmt

if __name__ == "__main__":
    a = QtGui.QApplication([])
    w = QtGui.QTableView()
    d = numpy.random.normal(0,1, (5, 1000,1000))
    for i in range(5):
        d[i, :, :] += i
    #m = NumpyArrayTableModel(fmt="%.5f")
    #m = NumpyArrayTableModel(None, numpy.arange(100.), fmt="%.5f")
    #m = NumpyArrayTableModel(None, numpy.ones((100,20)), fmt="%.5f")
    m = NumpyArrayTableModel(None, d, fmt="%.5f")
    w.setModel(m)
    m.setCurrentArrayIndex(4)
    #m.setArrayData(numpy.ones((100,)))
    w.show()
    a.exec_()
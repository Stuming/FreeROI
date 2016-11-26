# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""Implementation of a Tree model for subject data display.

"""

from treemodel import *


class TreeListModel(QAbstractItemModel):
    """Definition of class TreeListModel."""
    # customized signals
    repaint_surface = pyqtSignal()

    def __init__(self, subject, parent=None):
        """Initialize an instance."""
        super(TreeListModel, self).__init__(parent)
        self._data = subject
        self.hemi_list = []

    def get_data(self):
        return self._data

    def index(self, row, column, parent):
        """Return the index of item in the model."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        pass

    def parent(self, index):
        """Return the parent of the model item with the given index."""
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item in self._data:
            return QModelIndex()
        else:
            for hemi in self._data:
                if item in hemi.overlay_list:
                    return self.createIndex(self._data.index(hemi), 0, hemi)

    def rowCount(self, parent):
        """Return the number of rows for display."""
        if parent.isValid():
            if parent.internalPointer() in self._data:
                return self._data[parent.row()].overlay_count()
            else:
                return 0
        else:
            return len(self._data)

    def columnCount(self, parent):
        """Return the number of overlays in a hemispheres."""
        return 1

    def data(self, index, role):
        """Return specific data."""
        if not index.isValid():
            return None

        pass

    def flags(self, index):
        """Return the Qt flags for each data item."""
        if not index.isValid():
            return Qt.NoItemFlags

        pass

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return 'Name'
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return None

        pass

    def insertRow(self, row, item, parent):
        pass

    def removeRow(self, row, parent):
        pass

    def moveUp(self, index):
        pass

    def moveDown(self, index):
        pass

    def setCurrentIndex(self, index):
        """Set current row."""
        pass

    def is_hemisphere(self, index):
        """Check whether the `index` item is an instance of Hemisphere."""
        pass

    def _add_item(self, index, source):
        pass

    def _del_item(self, index, parent):
        pass


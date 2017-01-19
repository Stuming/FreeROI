#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from froi.core.dataobject import Hemisphere
from froi.core.subject import Subject
from treemodel import TreeModel
from froi.utils import *
from froi.core.labelconfig import LabelConfig

class SurfaceTreeView(QWidget):
    """Implementation a widget for layer selection and parameters alternating.
    """
    #current_changed = pyqtSignal()
    repaint_surface = pyqtSignal()
    builtin_colormap = ["Reds", "Greens", "Blues",
                        "Accent", "BrBG", "BuPu",
                        "Dark2", "GnBu", "Greys",
                        "OrRd", "Oranges", "PRGn",
                        "PuBu", "PuBuGn", "Purples",
                        "YlGn", "black-white", "blue-red",
                        "bone", "gray"]
    buildin_surf_list = ["White", "Pial", "Inflated", "Flatted"]
    buildin_hemi_list = ["Left", "Right", "Both"]

    def __init__(self, model, parent=None):
        """TreeView initialization."""
        super(SurfaceTreeView, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.setMaximumWidth(280)
        self._temp_dir = None
        self._icon_dir = get_icon_dir()

        self._init_gui()

        if isinstance(model, QAbstractItemModel):
            self._model = model
            self._tree_view.setModel(model)
        else:
            raise ValueError('Input must be a TreeModel!')

        self._create_action()

        self._set_combobox_hemi()
        self._set_combobox_surf()

    def _init_gui(self):
        """Initialize a GUI designation."""
        # initialize QTreeView
        self._tree_view = QTreeView()

        # initialize visibility controller
        visibility_label = QLabel('Visibility')
        self._visibility = QSlider(Qt.Horizontal)
        self._visibility.setMinimum(0)
        self._visibility.setMaximum(100)
        self._visibility.setSingleStep(5)
        visibility_layout = QHBoxLayout()
        visibility_layout.addWidget(visibility_label)
        visibility_layout.addWidget(self._visibility)

        # ComboBox for surface and hemisphere type option
        self._hemi_type = QComboBox()
        hemi_type = []  # self.buildin_hemi_list
        self._hemi_type.addItems(hemi_type)
        self._surf_type = QComboBox()
        surf_type = []  # self.buildin_surf_list
        self._surf_type.addItems(surf_type)

        # layout for Surface settings
        type_option_layout = QGridLayout()
        type_option_layout.addWidget(self._hemi_type, 1, 0)
        type_option_layout.addWidget(self._surf_type, 1, 1)
        type_option_group_box = QGroupBox('Type option')
        type_option_group_box.setLayout(type_option_layout)

        #-- Surface display settings panel
        # initialize Surface display settings widgets
        # TODO: to be refactorred
        surface_colormap_label = QLabel('Colormap:')
        self._surface_colormap = QComboBox()
        colormaps = self.builtin_colormap
        self._surface_colormap.addItems(colormaps)

        # layout for Surface settings
        surface_layout = QGridLayout()
        surface_layout.addWidget(surface_colormap_label, 1, 0)
        surface_layout.addWidget(self._surface_colormap, 1, 1)
        surface_group_box = QGroupBox('Surface colormap settings')
        surface_group_box.setLayout(surface_layout)

        #-- Overlay display settings panel
        # initialize up/down push button
        button_size = QSize(12, 12)
        self._up_button = QPushButton()
        self._up_button.setIcon(QIcon(os.path.join(self._icon_dir,
                                                   'arrow_up.png')))
        self._up_button.setIconSize(button_size)
        self._down_button = QPushButton()
        self._down_button.setIcon(QIcon(os.path.join(self._icon_dir,
                                                     'arrow_down.png')))
        self._down_button.setIconSize(button_size)

        # initialize ScalarData display settings widgets
        max_label = QLabel('Max:')
        self._view_max = QLineEdit()
        min_label = QLabel('Min:')
        self._view_min = QLineEdit()
        scalar_colormap_label = QLabel('Colormap:')
        self._scalar_colormap = QComboBox()
        colormaps = self.builtin_colormap
        self._scalar_colormap.addItems(colormaps)

        # layout for ScalarData settings
        scalar_layout = QGridLayout()
        scalar_layout.addWidget(max_label, 0, 0)
        scalar_layout.addWidget(self._view_max, 0, 1)
        scalar_layout.addWidget(self._up_button, 0, 2)
        scalar_layout.addWidget(min_label, 1, 0)
        scalar_layout.addWidget(self._view_min, 1, 1)
        scalar_layout.addWidget(self._down_button, 1, 2)
        scalar_layout.addWidget(scalar_colormap_label, 2, 0)
        scalar_layout.addWidget(self._scalar_colormap, 2, 1, 1, 2)
        scalar_group_box = QGroupBox('Overlay display settings')
        scalar_group_box.setLayout(scalar_layout)

        #-- layout config for whole TreeWidget
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self._tree_view)
        self.layout().addLayout(visibility_layout)
        self.layout().addWidget(type_option_group_box)
        self.layout().addWidget(surface_group_box)
        self.layout().addWidget(scalar_group_box)

        #-- right click context show
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu = QMenu(self)

    def showContextMenu(self):
        """Show right click context menu."""
        self.contextMenu.move(QCursor.pos())
        self.contextMenu.show()

    def _create_action(self):
        """Create several necessary actions."""
        # When select one item, display specific parameters
        self._tree_view.selectionModel().currentChanged.connect(
                self._disp_current_para)

        # TODO: fulfill this function
        ## When select one item, display its undo/redo settings
        #self._tree_view.selectionModel().currentChanged.connect(
        #        self.current_changed)

        # When dataset changed, refresh display.
        self._model.dataChanged.connect(self._disp_current_para)

        # When add new item, refresh display.
        self._model.rowsInserted.connect(self._disp_current_para)

        # When remove new item, refresh display.
        self._model.rowsRemoved.connect(self._disp_current_para)

        # When layout changed, refresh display.
        self._model.layoutChanged.connect(self._disp_current_para)

        # Config setting actions
        self._view_min.editingFinished.connect(self._set_view_min)
        self._view_max.editingFinished.connect(self._set_view_max)
        self._scalar_colormap.currentIndexChanged.connect(self._set_colormap)
        self._hemi_type.currentIndexChanged.connect(self._set_current_hemi)
        self._surf_type.currentIndexChanged.connect(self._set_current_surf)
        self._visibility.sliderReleased.connect(self._set_alpha)
        self._up_button.clicked.connect(self._up_action)
        self._down_button.clicked.connect(self._down_action)

        self._rightclick_add = self.contextMenu.addAction(u'Add')
        self._rightclick_edit = self.contextMenu.addAction(u'Edit')
        self._rightclick_del = self.contextMenu.addAction(u'Delete')
        self._rightclick_add.triggered.connect(self._rightclick_add_action)
        self._rightclick_edit.triggered.connect(self._rightclick_edit_action)
        self._rightclick_del.triggered.connect(self._rightclick_del_action)

    def _disp_current_para(self, index=-1):
        """Display selected item's parameters."""
        if index == -1:
            index = self._tree_view.currentIndex()

        if index.row() != -1:
            # set up status of up/down button
            if index.row() == 0:
                self._up_button.setEnabled(False)
            else:
                self._up_button.setEnabled(True)
            if index.row() == (self._model.rowCount(index.parent()) - 1):
                self._down_button.setEnabled(False)
            else:
                self._down_button.setEnabled(True)

            # min/max value
            self._view_min.setText(str(self._model.data(index, Qt.UserRole)))
            self._view_max.setText(str(self._model.data(index, Qt.UserRole + 1)))

            # colormap combo box setting
            cur_colormap = self._model.data(index, Qt.UserRole + 3)
            if isinstance(cur_colormap, LabelConfig):
                cur_colormap = cur_colormap.get_name()
            idx = self._scalar_colormap.findText(cur_colormap)
            self._scalar_colormap.setCurrentIndex(idx)

            # alpha slider setting
            current_alpha = self._model.data(index, Qt.UserRole + 2) * 100
            self._visibility.setValue(current_alpha)

            self._tree_view.setFocus()

            # Set current index
            self._model.setCurrentIndex(self._tree_view.currentIndex())

            self._set_combobox_hemi()
            self._set_combobox_surf()

    def _set_view_min(self):
        """Set current selected item's view_min value."""
        index = self._tree_view.currentIndex()
        value = self._view_min.text()
        if value == '':
            self._view_min.setText(str(self._model.data(index, Qt.UserRole)))
        else:
            self._model.setData(index, value, role=Qt.UserRole)

    def _set_view_max(self):
        """Set current selected item's view_max value."""
        index = self._tree_view.currentIndex()
        value = self._view_max.text()
        if value == '':
            self._view_max.setText(str(self._model.data(index, Qt.UserRole + 1)))
        else:
            self._model.setData(index, value, role=Qt.UserRole + 1)

    def _set_colormap(self):
        """Set colormap of current selected item."""
        index = self._tree_view.currentIndex()
        value = self._scalar_colormap.currentText()
        self._model.setData(index, value, role=Qt.UserRole + 3)

    def _set_combobox_hemi(self):
        """Set qcombobox hemisphere list."""
        subject = self._model.get_current_subject()
        # TODO
        if subject:
            hemi_list = subject.hemisphere_type
            self._hemi_type.clear()
            self._hemi_type.addItems(hemi_list)
            self._set_current_hemi()
        else:
            return

        '''
        AllItems = [self._hemi_type.itemText(i) for i in range(self._hemi_type.count())]
        for item in hemi_list:
            if item not in AllItems:
                self._hemi_type.addItem(item)
        '''

    def _set_current_hemi(self):
        """Set current hemisphere for display."""
        current_hemi_index = self._hemi_type.currentText().encode("ascii", 'ignore')
        self._model.setCurrentHemiIndex(current_hemi_index)
        return

    def _set_combobox_surf(self):
        """Set qcombobox surface list."""
        subject = self._model.get_current_subject()
        # TODO
        if subject:
            surf_list = subject.hemisphere[self._model.get_current_hemi_index()].get_surface_type()
            self._surf_type.clear()
            self._surf_type.addItems(surf_list)
            self._set_current_surf()
        else:
            return

        '''
        AllItems = [self._surf_type.itemText(i) for i in range(self._surf_type.count())]
        for item in surf_list:
            if item not in AllItems:
                self._surf_type.addItem(item)
        '''

    def _set_current_surf(self):
        """Set current surf for display."""
        current_surf_index = self._surf_type.currentText().encode("ascii", 'ignore')
        self._model.setCurrentSurfIndex(current_surf_index)
        return

    def _set_alpha(self):
        """Set alpha value of current selected item."""
        index = self._tree_view.currentIndex()
        value = self._visibility.value() / 100.
        self._model.setData(index, value, role=Qt.UserRole + 2)

    def _up_action(self):
        """Move selected item up for one step."""
        index = self._tree_view.currentIndex()
        self._model.moveUp(index)
        self._tree_view.setFocus()

    def _down_action(self):
        """Move selected item down for one step."""
        index = self._tree_view.currentIndex()
        self._model.moveDown(index)
        self._tree_view.setFocus()

    def _get_surface_index(self, surf_type):
        """Check different type of surface exist or not."""
        for index in self._tree_view.selectedIndexes():
            if index.data().endswith(surf_type):
                return index
        return -1

    def get_treeview(self):
        return self._tree_view

    def _rightclick_add_action(self):
        """Add, use method: main.py BpMainWindow._add_surface_image()"""
        print 'Add'

    def _rightclick_edit_action(self):
        """Edit"""
        print 'Edit'

    def _rightclick_del_action(self):
        """Del"""
        index = self._tree_view.currentIndex()
        parent = self._model.parent(index)
        print index.row()
        self._model.removeRow(index.row(), parent)
        self._disp_current_para()


    # def _add_item(self, source):
    #     index = self._tree_view.currentIndex()
    #     if not index.isValid():
    #         add_item = Hemisphere(source)
    #         ok = self._model.insertRow(index.row(), add_item, index)
    #
    #     else:
    #         parent = index.parent()
    #         if not parent.isValid():
    #             add_item = Hemisphere(source)
    #         else:
    #             parent_item = parent.internalPointer()
    #             parent_item.load_overlay(source)
    #             add_item = None
    #         ok = self._model.insertRow(index.row(), add_item, parent)
    #
    #     if ok:
    #         self._model.repaint_surface.emit()
    #         return True
    #     else:
    #         return False
    #
    # def _del_item(self, row, parent):
    #     index = self._tree_view.currentIndex()
    #     if not index.isValid():
    #         return False
    #     ok = self._model.removeRow(index.row(), index.parent())
    #     if ok:
    #         self._model.repaint_surface.emit()
    #         return True
    #     else:
    #         return False


if __name__ == '__main__':
    from froi import utils as froi_utils

    app = QApplication(sys.argv)
    db_dir = froi_utils.get_data_dir()
    # model init
    hemisphere_list = []
    sub1 = os.path.join(db_dir, 'surf', 'lh.white')
    surf2 = os.path.join(db_dir, 'surf', 'rh.white')

    h1 = subject(sub1)
    hemisphere_list.append(h1.hemi['lh'])

    model = TreeModel(hemisphere_list)

    # View init
    view = SurfaceTreeView(model)
    view.setWindowTitle("Hemisphere Tree Model")
    view.show()

    sys.exit(app.exec_())

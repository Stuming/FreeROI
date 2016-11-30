# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""
Dataset definition class for FreeROI GUI system.
"""

import re
import os
import sys

import nibabel as nib
import numpy as np
import gzip
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from nibabel.spatialimages import ImageFileError
from dataobject import Hemisphere


class subject(object):
    """Contain many surf data that from one subject."""
    def __init__(self, surf_path, offset=None):
        """Subject

        Parameters
        ----------
        surf_path: absolute surf file path
        offset: float | None
            If 0.0, the surface will be offset such that medial wall
            is aligned with the origin. If None, no offset will be
            applied. If != 0.0, an additional offset will be used.

        """
        self.hemi = {}
        self.hemi_type = []
        self.surfs_type = []
        self.add_hemi(surf_path)

    def __add_hemi(self, surf_path, offset=None):
        """Add hemi data and related info."""
        self.surf_path = surf_path
        (self.surf_dir, self.surf_name) = os.path.split(surf_path)
        current_hemi_type = self.surf_name.split('.')[0]
        current_surf_type = self.surf_name.split('.')[-1]
        self.hemi_type.append(current_hemi_type)
        self.surfs_type.append(current_surf_type)
        self.offset = offset

        self.hemi[current_hemi_type] = Hemisphere(surf_path)  # Here should add surf_type

    def add_hemi(self, surf_path):
        """Judge whether 'surf_path' is a valid data path."""
        if not os.path.exists(surf_path):
            print 'Surf file does not exist!'
            return None

        (surf_dir, surf_name) = os.path.split(surf_path)
        hemi_type = surf_name.split('.')[0]
        if self.is_hemi(hemi_type):
            self.__add_hemi(surf_path)
        else:
            print "Wrong hemisphere!"

    def del_hemi(self, hemi_type):
        """Delete hemisphere data."""
        if self.exist_hemi(hemi_type):
            self.hemi_type.remove(hemi_type)
            # To do: think about KeyError
            del self.hemi[hemi_type]
        else:
            print "Wrong hemisphere!"

    def del_surf(self, hemi_type, surf_type):
        """Delete surface data."""
        self.surfs_type.remove(surf_type)
        self.hemi[hemi_type].del_surfs(surf_type)

    def is_hemi(self, hemi_type):
        """Judge whether 'hemi_type' is a valid hemi type."""
        if hemi_type == 'lh' or hemi_type == 'rh':
            return True
        else:
            return False

    def exist_hemi(self, hemi_type):
        """Judge whether 'hemi_type' in 'self.hemi_type'."""
        if hemi_type in self.hemi_type:
            return True
        else:
            return False


if __name__ == '__main__':
    from froi import utils as froi_utils

    db_dir = froi_utils.get_data_dir()
    sub1 = os.path.join(db_dir, 'surf', 'lh.white')
    sub2 = os.path.join(db_dir, 'surf', 'rh.white')
    subject1 = subject(sub1)

    print subject1.hemi
    print subject1.exist_hemi('lh')
    subject1.add_hemi(sub2)
    print subject1.hemi
    subject1.del_hemi('lh')
    print subject1.hemi
    print subject1.exist_hemi('lh')

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


class Subject(object):
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
        self.name = surf_path.split('/')[-3]
        self.hemisphere = {}
        self.hemisphere_type = []
        self.visible = True
        self.add_hemisphere(surf_path)

    def __add_hemi(self, surf_path, offset=None):
        """Add hemi data and related info."""
        self.offset = offset
        (self.surf_dir, self.surf_name) = os.path.split(surf_path)
        current_hemi_type = self.surf_name.split('.')[0]

        if not self.hemisphere_type.count(current_hemi_type):
            self.hemisphere_type.append(current_hemi_type)

        # TODO Here should add surf_type
        self.hemisphere[current_hemi_type] = Hemisphere(surf_path)

    def add_hemisphere(self, surf_path):
        """Check whether 'surf_path' is a valid data path."""
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
        if self.hemisphere_type.count(hemi_type):
            self.hemisphere_type.remove(hemi_type)
            # To do: think about KeyError
            del self.hemisphere[hemi_type]
        else:
            print "Wrong hemisphere type!"

    def del_surf(self, hemi_type, surf_type):
        """Delete surface data."""
        return self.hemisphere[hemi_type].del_surfs(surf_type)

    def is_hemi(self, hemi_type):
        """Check whether 'hemi_type' is a valid hemi type."""
        if hemi_type == 'lh' or hemi_type == 'rh':
            return True
        else:
            return False

    def get_name(self):
        return self.name


if __name__ == '__main__':
    from froi import utils as froi_utils

    db_dir = froi_utils.get_data_dir()
    sub1 = os.path.join(db_dir, 'surf', 'lh.white')
    sub2 = os.path.join(db_dir, 'surf', 'rh.white')
    subject1 = subject(sub1)

    print subject1.hemisphere
    print subject1.hemisphere_type.count('lh')
    subject1.add_hemisphere(sub2)
    print subject1.hemisphere
    subject1.del_hemi('lh')
    print subject1.hemisphere
    print subject1.hemisphere_type.count('lh')

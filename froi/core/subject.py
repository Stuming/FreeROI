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
        self.surf_type = []
        if not os.path.exists(surf_path):
            print 'surf file does not exist!'
            return None
        self.surf_path = surf_path
        (self.surf_dir, surf_name) = os.path.split(surf_path)
        self.hemi_type = surf_name.split('.')[0]
        self.surf_type.append(surf_name.split('.')[1])
        self.hemi[self.hemi_type] = Hemisphere(surf_path)
        self.offset = offset

        self.name = surf_name  # Should be modified.

    def __add_hemi(self, surf_path, hemi_type):
        self.hemi[hemi_type] = Hemisphere(surf_path)  # Here should add surf_type

    def add_hemi(self, surf_path, hemi_type):
        if self.is_hemi(hemi_type):
            self.__add_hemi(surf_path, hemi_type)
        else:
            print "Wrong hemisphere!"

    def del_hemi(self, hemi_type):
        if self.is_hemi(hemi_type):  # To do: consider about KeyError
            del self.hemi[hemi_type]
        else:
            print "Wrong hemisphere!"

    def is_hemi(self, hemi_type):
        if hemi_type == 'lh' or hemi_type == 'rh':
            return True
        else:
            return False

    def get_suffix(self):
        return self.surf_type


if __name__ == '__main__':
    from froi import utils as froi_utils

    db_dir = froi_utils.get_data_dir()
    sub1 = os.path.join(db_dir, 'surf', 'lh.white')
    subject1 = subject(sub1)

    print subject1.hemi
    print subject1.is_hemi('lh')
    print subject1.surf_type
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


class subject:
    """Contain many surf data that from one subject."""
    def __init__(self):
        self.hemi = {}

    def __add_hemi(self, surf_path, hemi_type):
        self.hemi[hemi_type] = Hemisphere(surf_path)  # Here should add surf_type

    def add_hemi(self, surf_path, hemi_type):
        if self.is_hemi(hemi_type):
            self.__add_hemi(surf_path, hemi_type)

    def del_hemi(self, hemi_type):
        if self.is_hemi(hemi_type):  # To do: consider about KeyError
            del self.hemi[hemi_type]
        else:
            print "Wrong hemisphere!"

    def is_hemi(self, hemi_type):
        if hemi_type == 'left' or hemi_type == 'right':
            return True
        else:
            return False

if __name__ == '__main__':
    from froi import utils as froi_utils

    subject1 = subject()
    db_dir = froi_utils.get_data_dir()
    sub1 = os.path.join(db_dir, 'surf', 'lh.white')
    subject1.add_hemi(sub1, 'left')

    print subject1.hemi
    subject1.del_hemi('left')
    print subject1.hemi

# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : CDEyes.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/07/30 00:52:02
#   desc     : 
#              
# ==========================================================================

import os, sys, time
sys.path.append('./')

from src.DesktopEye import DesktopEye


class CDEyes(object):
    def __init__(self) -> None:
        self.desktop_eye = DesktopEye()
        pass


if __name__ == '__main__':
    eye = CDEyes()


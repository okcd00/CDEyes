# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : DesktopEye.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/07/30 00:54:30
#   desc     : 
#              
# ==========================================================================

import os
import sys
import time
import random
import datetime
from PIL import Image

# import win32 packages
import win32ui
import win32gui
import win32api
import win32con
import win32print
from ctypes import windll


def time_identifier():
    """
    基于当前时间获取时间戳文件名后缀，单双数位混淆版
    """
    time_stamp = '{0:%m%d%H%M%S%f}'.format(datetime.datetime.now())[::-1]
    mask = map(
        lambda x: chr(ord(x[0]) + ord(x[1])), 
        zip(time_stamp[::2], time_stamp[1::2]))
    return ''.join(mask) + ''.join([str(random.randint(1, 10)) for _ in range(2)])


class DesktopEye(object):
    desktop = win32gui.GetDesktopWindow()

    def __init__(self, project_path='./', debug=False):
        self.project_path = project_path
        self.debug = debug
        self.dpi = self._calculate_dpi()        

        # desktop size
        self.left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.right = self.left + self.width

        self.top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        self.height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        self.bottom = self.top + self.height

        self.left, self.top, self.right, self.bottom = self._transform_as_dpi(
            (self.left, self.top, self.right, self.bottom))
        self.position = (self.left, self.top, self.right, self.bottom)
        self.log("Desktop Size:", self.position)

        self.save_dir = os.path.join(project_path, 'data')

    @staticmethod
    def show_all_hwnd():
        hwnd_title = {}

        def get_all_hwnd(hwnd, mouse):
            if (win32gui.IsWindow(hwnd)
                    and win32gui.IsWindowEnabled(hwnd)
                    and win32gui.IsWindowVisible(hwnd)):
                hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(get_all_hwnd, 0)
        for h, t in hwnd_title.items():
            if t:
                print(h, t)

    def log(self, *args):
        if self.debug:
            print(*args)

    def save_fig(self, image, save_dir=None, postfix='jpg', quality=75):
        form_dict = {
            'jpg': 'JPEG',
            'png': 'PNG'
        }
        save_dir = save_dir or self.save_dir
        time_str = time.strftime('%y%m%d_%H%M%S', time.localtime())
        file_path = 'screenshot_{}.{}'.format(time_str, postfix)
        dump_path = os.path.join(save_dir, file_path)

        form = form_dict.get(postfix.lower(), 'jpg')
        image.save(fp=dump_path, format=form, quality=quality)

        self.log('Dump screenshot as {}'.format(dump_path))
        return dump_path

    def load_fig(self, path):
        valid_flag = True
        try:
            image = Image.open(path)
            return image, valid_flag
        except Exception as e:
            valid_flag = False
            if self.debug:
                print(e)
        return None, valid_flag

    def _calculate_dpi(self):
        hDC = win32gui.GetDC(0)
        real_width = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        real_height = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
        cur_width = win32api.GetSystemMetrics(0)
        cur_height = win32api.GetSystemMetrics(1)
        self.log(real_width, 'x', real_height, '->', cur_width, 'x', cur_height)
        return round(real_width / cur_width, 2)

    def _transform_as_dpi(self, position_case):
        left, top, right, bottom = [int(p * self.dpi) for p in position_case]
        return left, top, right, bottom

    def _get_handle_position(self, handle):
        left, top, right, bottom = self._transform_as_dpi(win32gui.GetWindowRect(handle))
        self.log(handle, ':', left, top, right, bottom)
        return left, top, right, bottom

    def dump_handle_capture(self, handle, dump_path=None, position_case=None, remove_title_bar=True, debug=False):
        """
        基于句柄获取图像并保存至文件，
        返回句柄截图的文件名。
        """
        # position and size
        if position_case:
            left, top, right, bottom, width, height = position_case
        else:
            left, top, right, bottom = self._get_handle_position(handle)
            width, height = right - left, bottom - top

        # 创建设备描述表
        desktop_dc = win32gui.GetWindowDC(handle)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)

        # 创建内存设备描述表
        mem_dc = img_dc.CreateCompatibleDC()

        # 创建位图对象
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        # 截图至内存设备描述表
        mem_dc.BitBlt(
            (0, 0), (width, height),
            img_dc, (left, top), win32con.SRCCOPY)
            # img_dc, (0, 0), win32con.SRCCOPY)
        result = windll.user32.PrintWindow(handle, mem_dc.GetSafeHdc(), int(remove_title_bar))
        self.log('mem_dc.GetSafeHdc:', result)

        # 存入bitmap临时文件
        tmp_path = dump_path or os.path.join(
            self.save_dir, time_identifier() + '.bmp')
        self.log('save source to {}'.format(tmp_path))
        screenshot.SaveBitmapFile(mem_dc, tmp_path)
        # bmp_str = screenshot.GetBitmapBits(True)

        # 内存释放
        win32gui.DeleteObject(screenshot.GetHandle())
        mem_dc.DeleteDC()
        img_dc.DeleteDC()
        win32gui.ReleaseDC(handle, desktop_dc)
        return tmp_path

    def _get_handle_screenshot(self, handle, method='handle'):
        if method == 'desktop':
            left, top, right, bottom = self.position
            width, height = self.width, self.height
        else:  # 'window'/'handle'
            left, top, right, bottom = self._get_handle_position(handle)
            width, height = right - left, bottom - top

        position_case = (left, top, right, bottom, width, height)
        tmp_path = self.dump_handle_capture(
            handle, position_case=position_case, 
            remove_title_bar=False, debug=self.debug)
        return tmp_path

    def _get_desktop_screenshot(self):
        tmp_path = self._get_handle_screenshot(self.desktop, method='desktop')
        return tmp_path

    def capture_by_handle(self, handle, save_dir=None, postfix='jpg'):
        """
        输入窗体句柄，获取图像及保存地址
        """
        if save_dir is not None:
            self.save_dir = save_dir
        if not isinstance(handle, int):
            return self.capture_by_name(
                window_name=handle, save_dir=save_dir, postfix=postfix)
        
        tmp_path = self._get_handle_screenshot(handle, method='window')
        image, valid_flag = self.load_fig(tmp_path)
        if not valid_flag:
            self.log(f"Failed in load_fig({tmp_path})")
            
        if postfix.lower() != 'bmp':
            dump_path = self.save_fig(
                image=image, save_dir=save_dir, postfix=postfix)
            # Remove bitmap
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return image, dump_path

    def capture_by_name(self, window_name, save_dir=None, postfix='jpg'):
        """
        输入窗体名称，获取图像及保存地址
        """
        if save_dir is not None:
            self.save_dir = save_dir
        handle = win32gui.FindWindow(None, window_name)
        return self.capture_by_handle(
            handle=handle, save_dir=save_dir, postfix=postfix)

    def capture(self, name_or_handle, save_dir=None, postfix='jpg'):
        if isinstance(name_or_handle, int):
            return self.capture_by_handle(
                handle=name_or_handle, save_dir=save_dir, postfix=postfix)
        elif isinstance(name_or_handle, str):
            return self.capture_by_name(
                window_name=name_or_handle, save_dir=save_dir, postfix=postfix)
        else:
            raise ValueError("Invalid input as `name_or_handle`, should be a handle number or a string as a window name.")

    def __call__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    de = DesktopEye(debug=True)
    # de.capture(u'最终幻想XIV')
    # de.show_all_hwnd()
    de.capture(u'*new 1 - Notepad++')


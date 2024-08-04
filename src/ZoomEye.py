# ==========================================================================
#   Copyright (C) since 2020 All rights reserved.
#
#   filename : ZoomEye.py
#   author   : chendian / okcd00@qq.com
#   date     : 2022-10-25
#   desc     : Zoom in the view around the mouse.
# ==========================================================================

import win32gui
import win32api
import win32con
import win32print

import tkinter
import threading  # 导入多线程模块
from PIL import ImageGrab, ImageTk
from pynput import mouse


class ZoomEye(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.dpi = self._calculate_dpi()
        root = tkinter.Tk()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # 放大镜窗口大小
        self.zoom_area_width = 500
        self.zoom_area_height = 300
        self.zoom_area_position = (self.zoom_area_width, self.zoom_area_height)
        root.geometry(f"{self.zoom_area_width}x{self.zoom_area_height}")

         # [1] 置顶
        root.wm_attributes('-topmost', 1) 
        root.overrideredirect(True)  # 不显示标题栏
        
        self.immg = None
        self.root = root
        self.canvas = None
        self.event = threading.Event()
        self.event.clear()
        # self.mouse_event = PyMouseEvent(capture=True)
        self.mouse_event = mouse.Listener(on_click=True)
        self.mouse_right_is_down = False

    def log(self, *args):
        if self.debug:
            print(*args)

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

    def run(self):
        # [2] 全局化图像对象，避免销毁导致闪烁
        global immg       
        self.draw_zoom()

    def draw_zoom(self):                 
        # 获取鼠标坐标
        x, y = win32api.GetCursorPos()      
        _w, _d = self.zoom_area_width // 10, self.zoom_area_height // 10
        zoom_area = self._transform_as_dpi((x-_w,y-_d,x+_w,y+_d))   
        img = ImageGrab.grab(zoom_area)

        # 全屏抓取
        self.immg = ImageTk.PhotoImage(img.resize(self.zoom_area_position))     

        # 画布从中心点开始绘制
        _x, _y = self.zoom_area_width // 2, self.zoom_area_height // 2
        self.canvas.create_image(_x, _y, image=self.immg) 

        # 不断刷新放大镜的位置 (追加：如果越界则翻转)
        x -= self.zoom_area_width + _w if x + _w + self.zoom_area_width >= self.screen_width else - _w
        y -= self.zoom_area_height + _d if y+_d + self.zoom_area_height >= self.screen_height else - _d
        self.root.geometry("{}{}{}{}{}{}{}".format(
            self.zoom_area_width, "x", self.zoom_area_height, "+", x, "+", y))
        self.root.after(func=self.run, ms=10)

    def paint(self):
        # 创建白色画布
        self.canvas = tkinter.Canvas(
            master=self.root, 
            width=self.zoom_area_width, 
            height=self.zoom_area_height)     
        
        # 画布放置至窗体
        self.canvas.pack(
            fill=tkinter.BOTH, 
            expand=tkinter.YES)      

    def run_test_listener(self):
        if self.mouse_right_is_down:
            self.draw_zoom()
        self.mouse_right_is_down = False

    def left_click_down(self):
        print("left click")
        self.mouse_left_is_down = True

    def right_click_down(self):
        print("right click")
        self.mouse_right_is_down = True

    def __call__(self):
        self.root.after(func=self.run, ms=100)
        self.paint()

        # 开始循环
        self.root.mainloop()


if __name__ == "__main__":
    ze = ZoomEye()
    ze()

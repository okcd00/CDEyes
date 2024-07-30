# coding: utf-8
# ==========================================================================
#   Copyright (C) since 2024 All rights reserved.
#
#   filename : GamepadEye.py
#   author   : chendian / okcd00@qq.com
#   date     : 2024/07/31 01:07:32
#   desc     : 
#              
# ==========================================================================
import os
import time
import pathlib, urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options=Options()
chrome_options.add_argument("--window-size=1920x1080") # windowsize
chrome_options.add_argument('--disable-gpu') # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--hide-scrollbars') # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('--disable-web-security') # 禁用网页安全性功能，用于解决跨域问题
chrome_options.add_argument('--disable-infobars') # 禁用"Chrome正在受到自动软件的控制"的提示

driver=webdriver.Chrome(options=chrome_options)

path = './assets/gamepad/Xbox - 游戏手柄指令显示面板.html'
cur_dir = os.getcwd()
abs_path = os.path.abspath(os.path.join(cur_dir, path))
file_path = urllib.parse.urlunparse(('file', '', abs_path, '', '', ''))
print(file_path)
driver.get(file_path)
time.sleep(20)
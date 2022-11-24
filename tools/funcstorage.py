import os, msvcrt, time, pyautogui, numpy
import cv2 as cv
import numpy as np
from cv2 import TM_CCOEFF_NORMED



# clears console, can be delayed by an argument integer 
def clear_console(delay=0):
    time.sleep(delay)
    os.system('cls')


# stops the program until it receives an input, then held in inputKey variable
def freeze_wait_for_input():
    input_key = msvcrt.getch().decode('utf-8')
    return input_key


# captures a window preview of a certain window 
# if arg is None will screenshot entire screen
def window_capture(window=None):
    import win32gui, win32ui, win32con


    if window:
        if type(window)==int:
            window = win32gui.GetWindowText(window)
        hwnd = win32gui.FindWindow(None, str(window))
        window_nr = win32gui.FindWindow(None, str(window))
        window_rect = win32gui.GetWindowRect(window_nr)
        w, h = window_rect[2] - window_rect[0], window_rect[3] - window_rect[1]
    #if window is not detected, it will just use a screenshot
    else:
        hwnd = None
        w, h = pyautogui.size()
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)

    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = numpy.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h, w, 4)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    img = img[...,:3]
    
    return img



class Assets:
    asset_list = []
    def __init__(self, path, method=TM_CCOEFF_NORMED):
        self.method = method
        self.asset_img = cv.imread(path, method)
        self.width = self.asset_img.shape[0]
        self.height = self.asset_img.shape[1]
        self.asset_list.append(self)

    def get_match_list(self, confidence):
        result = cv.matchTemplate(window_capture(None), self.asset_img, self.method)
        detections = numpy.where(result >= 0.80)
        detections = list(zip(detections[1], detections[0]))



# returns whether an object is present within a screenshot
def check_if_obj_present(screenshot, obj, threshold=0.35): 
    result = cv.matchTemplate(screenshot, obj, cv.TM_CCOEFF_NORMED) 
    result = np.where(result>threshold) 
    if len(result[0]): 
        return True 
    else: 
        return False 



# returns which Timberman map is present on the screen right now
def check_map(hwnd=None):
    # retries itself 100 times
    for retries in range(100):
        trunk_assets_dir = r'assets\trunks'
        ss_crop = crop_img(window_capture(hwnd), 0.3,0.7,0.03,0.85)
        for trunk_name in os.listdir(trunk_assets_dir):
            trunk_img = cv.imread('{}\{}'.format(trunk_assets_dir,trunk_name))
            if check_if_obj_present(ss_crop, trunk_img, 0.9):
                if 'fat' in trunk_name: 
                    return 'fat'
                elif 'natural' in trunk_name:
                    return 'natural'
        if retries % 21==0:
            print('cannot detect map type, retrying\nmake sure you are in a pregame screen')
        time.sleep(0.25)




# crops an image 
def crop_img(img, x_start=0, x_end=1, y_start=0, y_end=1):
    x = img.shape[1]
    y = img.shape[0]
    cropped_img = img[int(y*y_start):int(y*y_end),  # Y asis crop
                      int(x*x_start):int(x*x_end)]  # X asis crop
    return cropped_img



def restart_script(cwd):
    os.system(cwd)
    exit()
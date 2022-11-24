import win32gui, win32com.client, keyboard, time, os
import cv2 as cv
from tools.funcstorage import (freeze_wait_for_input, clear_console, window_capture, 
                               check_if_obj_present, crop_img, check_map)


# used for restarting the script in certain situations
cwd = os.getcwd()+r'\timberman_script.py'

print('''\n        Finding Timberman window...\n''')
hwnd = win32gui.FindWindow(None, str('timberman'))

# loops the print until a valid input is received
if hwnd: 
    while True:
        print('''        Game's presence confirmed\n
    1920x1080 resolution is most recommended \n
    the script will shut itself down when Timberman is closed
    or when [ Ctrl + C ] is pressed\n \n \n
    Press [ 1 ] to start the script\n
    Press [ q ] to go exit''')
        inputkey = freeze_wait_for_input()
        match inputkey.lower():
            case '1':
                break
            case 'q':
                exit()
            case _:
                pass
else: 
    while True:
        print('''        Game's window not found
        If the issue persists, contact the bot owner on GitHub as this might be OS specific\n \n
    Press [ 1 ] to run the setup again\n
    Press [ q ] to go back to main menu''')

        inputkey = freeze_wait_for_input()
        match inputkey.lower():
            case '1':
                print('    Retrying...')
                time.sleep(1)
                os.system(cwd)
            case 'q':
                exit()
            case _:
                pass

clear_console(1)
# game's state will be based on whether life bar is visible on screen 
life_bar = cv.imread(r'assets\menu_nav\life_bar.jpg', cv.IMREAD_UNCHANGED)
life_bar = cv.Canny(life_bar,100,200)
game_over = cv.imread(r'assets\menu_nav\game_over.jpg')
game_over = cv.Canny(game_over,100,200)

shell = win32com.client.Dispatch("WScript.Shell")
shell.SendKeys('%')
win32gui.SetForegroundWindow(hwnd)
tree_assets_dir = r'assets\branches'


# main loop persists until the game window is not on PC anymore
while hwnd:

    # prevents from starting the loop if life bar is not visible 
    screenshot = crop_img(window_capture(hwnd),  0.2,0.8,  0.03,0.85)
    while not check_if_obj_present(cv.Canny(screenshot,100,200), life_bar, 0.38):
        print('\nwaiting for the singleplayer game to start manually\n')
        time.sleep(3)
        screenshot = crop_img(window_capture(hwnd),  0.3,0.7,  0.01,0.4)

    # loading left and right branch images based on map type detected
    branches_left = {}
    branches_right = {}
    match check_map(hwnd):
        case 'natural':
            print('map detected: thin branch type')
            for file_name in os.listdir(tree_assets_dir):
                if 'thin' in file_name:
                    file = '{}\{}'.format(tree_assets_dir, file_name)
                    branch = cv.imread(file, cv.IMREAD_UNCHANGED)
                    if 'left' in file: branches_left[file_name] = branch
                    elif 'right' in file: branches_right[file_name] = branch
                    threshold = 0.35 #TO BE ADJUSTED !!!

        case 'fat':
            print('map detected: thick branch type')
            for file_name in os.listdir(tree_assets_dir):
                if 'fat' in file_name:
                    file = '{}\{}'.format(tree_assets_dir, file_name)
                    branch = cv.imread(file, cv.IMREAD_UNCHANGED)
                    if 'left' in file: branches_left[file_name] = branch
                    elif 'right' in file: branches_right[file_name] = branch
                    threshold = 0.3

        case _:
            print('cannot detect map type, returning to main menu')
            time.sleep(2)
            exit()

    # focusing the game window if map type has been found
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    last = 'a'

    # MAIN LEFT\RIGHT PLAYING LOOP
    # loops if life bar is visible and window present on PC
    while check_if_obj_present(cv.Canny(screenshot,100,200), life_bar, 0.38) and hwnd:
        screenshot = crop_img(window_capture(hwnd),0.25,0.75, 0.52,0.66)
        hwnd = win32gui.FindWindow(None, str('timberman'))

        screenshot = crop_img(window_capture(hwnd), 0.25,0.75, 0.52,0.66)
        left_half = crop_img(screenshot, x_end=0.5)
        right_half = crop_img(screenshot, x_start=0.5)

        skip = False

        # presses D if a branch has been discovered on left side
        for branch_L in branches_left:
            if check_if_obj_present(left_half, branches_left[branch_L], threshold):
                print('left side branch detected: {}'.format(branch_L))
                keyboard.press_and_release('d')
                time.sleep(0.02)
                keyboard.press_and_release('d')
                time.sleep(0.03)
                last = 'd'
                skip = True
                break

        # presses A if a branch has been discovered on right side
        for branch_R in branches_right:
            if check_if_obj_present(right_half, branches_right[branch_R], threshold):
                print('right side branch detected: {}'.format(branch_R))
                keyboard.press_and_release('a')
                time.sleep(0.02)
                keyboard.press_and_release('a')
                time.sleep(0.03)
                last = 'a'
                skip = True
                break
        

        if not skip:
            print('no branch on either side')
            keyboard.press_and_release(last)
            
        time.sleep(0.05)

    
        screenshot = crop_img(window_capture(hwnd), 0.3, 0.7)


    #checking if the game is still running in between loops, if not: break
    hwnd = win32gui.FindWindow(None, str('timberman'))





time.sleep(1.5)
while True:
    print('''===================  TASK DONE  ===================\n \n
Press [ 1 ] to run it again\n
Press [ q ] to go back to main menu''')

    inputkey = freeze_wait_for_input()
    clear_console()
    match inputkey.lower():
        case '1':
            os.system(cwd)
        case 'q':
            exit()
        case _:
            pass
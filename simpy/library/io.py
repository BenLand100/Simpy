#  Copyright 2022 by Benjamin J. Land (a.k.a. BenLand100)
#
#  This file is part of Simpy.
#
#  Simpy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Simpy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Simpy.  If not, see <https://www.gnu.org/licenses/>.

import pyautogui
import time
import numpy as np

from .global_vals import *

def sleep(sec):
    time.sleep(sec)
    
def mark_time():
    return time.monotonic()
    
def move_mouse(x,y,speed=None):
    '''moves the mouse to a point'''
    if speed is None:
        ex,ey = x+client_x,y+client_y
        pyautogui.moveTo(ex,ey,_pause=False)
    else:
        cx,cy = pyautogui.position()
        ex,ey = x+client_x,y+client_y
        dt = np.sqrt((cx-x)**2.0+(cy-y)**2.0)/(speed*1000)
        pyautogui.moveTo(ex,ey,dt,pyautogui.easeOutQuad)
        
def wind_mouse(x,y,speed=10,**kwargs):
    cx,cy = pyautogui.position()
    ex,ey = x+client_x,y+client_y
    def move_mouse(x,y):
        if speed:
            cx,cy = pyautogui.position()
            time.sleep(np.sqrt((cx-x)**2.0+(cy-y)**2.0)/(speed*1000))
        pyautogui.moveTo(x,y,_pause=False)
    _wind_mouse(cx,cy,ex,ey,move_mouse=move_mouse,**kwargs)


sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)

def _wind_mouse(start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12, move_mouse=lambda x,y: None):
    '''
    WindMouse algorithm. Calls the move_mouse kwarg with each new step.
    Released under the terms of the GPLv3 license.
    G_0 - magnitude of the gravitational fornce
    W_0 - magnitude of the wind force fluctuations
    M_0 - maximum step size (velocity clip threshold)
    D_0 - distance where wind behavior changes from random to damped
    '''
    current_x,current_y = start_x,start_y
    v_x = v_y = W_x = W_y = 0
    while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
        W_mag = min(W_0, dist)
        if dist >= D_0:
            W_x = W_x/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
            W_y = W_y/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
        else:
            W_x /= sqrt3
            W_y /= sqrt3
            if M_0 < 3:
                M_0 = np.random.random()*3 + 3
            else:
                M_0 /= sqrt5
        v_x += W_x + G_0*(dest_x-start_x)/dist
        v_y += W_y + G_0*(dest_y-start_y)/dist
        v_mag = np.hypot(v_x, v_y)
        if v_mag > M_0:
            v_clip = M_0/2 + np.random.random()*M_0/2
            v_x = (v_x/v_mag) * v_clip
            v_y = (v_y/v_mag) * v_clip
        start_x += v_x
        start_y += v_y
        move_x = int(np.round(start_x))
        move_y = int(np.round(start_y))
        if current_x != move_x or current_y != move_y:
            #This should wait for the mouse polling interval
            move_mouse(current_x:=move_x,current_y:=move_y)
    return current_x,current_y

def click_mouse(x,y,left=True,speed=None):
    '''moves to and clicks a point'''
    move_mouse(x,y,speed=speed)
    pyautogui.click(button='left' if left else 'right')
    
def send_keys(text,speed=1.0):
    '''sends text to the client (\n for enter)'''
    pyautogui.typewrite(text,interval=0.05*speed)
    
def get_client(region=None):
    '''region should be (x,y,w,h) or match the pyautogui.screenshot docs
       returns a numpy array represnting the image in the region'''
    return np.asarray(pyautogui.screenshot(region=region))

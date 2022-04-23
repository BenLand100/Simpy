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

from .bitmap import load_image,find_bitmap

#set by set_client_region() used throughout.
client_x,client_y = 0,0
client_w,client_h = pyautogui.size()

#constant config
pyautogui.PAUSE = 0.1

def set_client_region(x,y,w,h):
    '''looks for the client and caches its location'''
    client_x,client_y = x,y
    client_w,client_h = w,h

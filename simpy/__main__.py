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

from .simpy import Simpy

from PyQt5.QtWidgets import QApplication

import sys
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    simpy = Simpy(app=app)   
    simpy.show()     
    
    #pythonpath = [os.path.join(simpy.app_path,"library")]
    #if 'PYTHONPATH' in os.environ:
    #    pythonpath.append(os.environ['PYTHONPATH'])
    #os.environ['PYTHONPATH'] = ':'.join(pythonpath)
    #print(os.environ['PYTHONPATH'])
    
    if len(sys.argv) > 1:
        win.open_file(sys.argv[1]) #chdir's on its own
    else:
        #os.chdir(os.path.expanduser('~')) 
        #assuming we're installed from a cloned repo...
        os.chdir(os.path.join(simpy.app_path,'../examples'))

    sys.exit(app.exec_())


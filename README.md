# Simpy

![Simpy](simpy/icons/simpy_128x128.png)

Simpy is a minimal clone of the popular automation utility 
[Simba](https://github.com/MerlijnWajer/Simba), writen in Python and targeting 
Python as a scripting language. 

## Installing

Installing [Python 3.8+](https://www.python.org/downloads/) is required. You may
find it easier to install a more integrated Python environment like 
[Anaconda](https://www.anaconda.com/products/distribution) or whatever is 
provided by your system repository. You will also need `git`, which can be
installed within Anaconda, if necessary.

With those prereqs, first clone this repository:

```
git clone https://github.com/BenLand100/Simpy
```

And then install with pip:

```
pip install --user -e Simpy
```

This will create an editable installation that will link to the cloned git repo. 
This means the Simpy code installed on your system will automatically be updated
if the repo is updated or edited.

Reinstallation may still be necessary if there are new dependencies.

## Usage


Simpy is a minimal IDE that runs Python scripts. Figuring out how to launch it 
on your platform is the most complicated step. Then open/write a script and press 
`Run` on the toolbar to run it. You can probably figure out how to use it from 
there without further instructions.

### Linux / OSX

After installing, you can run the program `Simpy` to launch the GUI. It will 
also open a file as an argument. 

### Windows / Cross-platform

After installing, you can execute the `simpy` python module.

```
python3 -m simpy
```

## Screenshots

Simpy will adapt to your system theme.

![Simpy on a light theme](screenshots/simpy_light.png)

![Simpy on a dark theme](screenshots/simpy_dark.png)

## Distributing

The `package.sh` and `package.bat` scripts can run [PyInstaller](https://pyinstaller.org/en/stable/)
to create a single-file distributable version of Simpy. Must be run on the 
targeted platform.

## Copying

Copyright 2021 by Benjamin J. Land (a.k.a. BenLand100). 

Released under the GPLv3 license.

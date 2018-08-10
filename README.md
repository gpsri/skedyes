# skedyes
OEMS-1808 PC TOOL
sudo apt-get install python3.4-dev
sudo apt-get install qt4-dev-tools libqt4-dev libqt4-core libqt4-gui 
sudo apt-get install build-essential libssl-dev libffi-dev python-dev

sudo python3.4 configure.py

1. download sip from Riverbank Computing [https://www.riverbankcomputing.com/software/sip/download]
2. download PyQT from Riverbank Computing [https://www.riverbankcomputing.com/software/pyqt/download]
3. In the terminal run: sudo apt-get install python3.4-dev build-essential qt4-dev-tools libqt4-dev libqt4-core libqt4-gui ibssl-dev libffi-dev python-dev
4. Browse the folder in which you downloaded sip and extract the archive. Now browse to the extracted folder using the terninal ( eample, go to cd /home/user/Downloads/sip/
5. In the terminal run: sudo python3.4 configure.py
6. In the terminal run: sudo make
7. In the terminal run: sudo make install
8. Extract the PyQt archive you downloaded. Now browse to the extracted PyQt folder in the terminal
9. In the terminal run:  sudo python3.4 configure.py

		Do you accept the terms of the license? yes 
10. In the terminal run:  sudo make
11. In the terminal run: sudo make install

PyQt4 is now installed on your computer.

sudo apt-get install python-pip 

sudo pip install --upgrade pip 

sudo pip install --upgrade virtualenv

sudo pip install pyinstaller 

pyinstaller --onefile helloworld.pyls

sudo apt-get install gtk2-engines
sudo apt-get install gtk2-engines-*
sudo apt-get install libgtkmm-2.4-1c2
sudo apt-get install libcanberra-gtk-module




As mentioned by other answerers, the cross-compilation feature is removed from PyInstaller since 1.5. Here, show how to package a Windows executable from Python scripts using PyInstaller under wine.

Step 1: Install wine and Python
sudo apt-get install wine
wine msiexec /i python-2.7.10.msi /L*v log.txt
PS: Newer Python versions already include pip (is used to install pyinstaller). Download Python installation package from here (e.g., python-2.7.10.msi)

Step 2: Install PyInstaller on wine
$ cd ~/.wine/drive_c/Python27
$ wine python.exe Scripts/pip.exe install pyinstaller

Successfully installed pyinstaller-3.1.1 pypiwin32-219
Step 3: Package Python scripts
Package Python scripts (e.g., HelloWorld.py) with pyinstaller.

$ wine ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile HelloWorld.py

# filename: HelloWorld.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-

print('Hello World!')
The Windows executable file is located in dist/.

$ wine dist/HelloWorld.exe 
Hello World!
fixme:msvcrt:__clean_type_info_names_internal (0x1e24e5b8) stub

just-dice-bot
=============

Hi, i just made a quick prototype to martingale on just-dice.com. Feel free to use it under GPL. If you want to donate some Satoshis: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83 Thanks.

HOW IT WORKS
-------------
Just-dice has no api. What is used here is remoting the website with selenium. We run selenium in an 


INSTALL
-------------

It's tested on python 2.7 on linux. 
I installed these:

```
aptitude install firefox xvfb xterm xserver-xephyr fvwm
xhost +
pip install selenium
pip install PyVirtualDisplay
pip install EasyProcess
```

On windows, install Python 2.7, Selenium and Firefox. Here in Detail:
```
* Python 2.7:
  Download and install http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi
* Requirements to run Selenium in python:
  We need some modules in python. first: setuptools and pip:
    Install http://www.lfd.uci.edu/~gohlke/pythonlibs/2ydk2k2o/setuptools-0.9.7.win32-py2.7.exe
	Install http://www.lfd.uci.edu/~gohlke/pythonlibs/2ydk2k2o/pip-1.4.win32-py2.7.exe
Selenium: 	http://docs.seleniumhq.org/download/
  #open a cmd box:
  Start menu - search for 'cmd' - open cmd.exe
  #in cmd type (and press Return after each line):
    #change to the dir where pip.exe is in, usually:
	cd \python27\scripts
	#install selenium module for python
    pip install -U selenium
  Firefox: 	
    Install firefox from https://www.mozilla.org/en-US/firefox/fx/#desktop
* Config:
  copy config-DEFAULT.py to config.py
  edit your config.py with an text editor (your user/password, ...)
* Start:
  doubleclick on 'start.bat'
```

Please tell me if something is missing.

CONFIG
-------------

Copy config-DEFAULT.py to config.py. Then just edit some vars in config.py, they are good commented.

RUN
-------------

python just-dice-bot.py

ON ERRORS
-------------

* make sure, you have the latest version
* open your config, set visible=1
* explain, what you expect the bot to do (the error)
* explain, what you see and what the bot does
* describe your system (linux/windows, python version, ...)
* copy the stack trace from command line if any
* report on github: https://github.com/KgBC/just-dice-bot/issues

LICENSE
-------------

GPLv2 applies. Please refer to this project:
https://github.com/KgBC/just-dice-bot

DONATE
-------------

Send your satoshi's to: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83
Thanks.

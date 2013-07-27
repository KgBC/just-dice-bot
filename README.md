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

On windows, install Python 2.7, Tor Browser and Selenium. That should do it.
```
Python:		http://www.python.org/download/
Tor Bundle: https://www.torproject.org/projects/torbrowser.html.en
Selenium: 	http://docs.seleniumhq.org/download/
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

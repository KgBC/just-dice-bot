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
aptitude install firefox xvfb xterm xserver-xephyr
xhost +
pip install selenium
pip install PyVirtualDisplay
pip install EasyProcess
```

On windows, install Python 2.7, Tor Browser and Selenium. That should do it.
Python:		http://www.python.org/download/
Tor Bundle: https://www.torproject.org/projects/torbrowser.html.en
Selenium: 	http://docs.seleniumhq.org/download/

Please tell me if something is missing.

CONFIG
-------------

is done in the .py file itself. Just edit some vars:

```
# if you want to see what is happening set to 1:
self.visible = 0

# bot failed after losing X rounds. Start bet is changed on that.
# If no bet is possible with this setting, it uses 0.00000001 as start bet.
self.lose_rounds = 13 # about 0.1 % risk

# which chance to play:
self.chance=49.5

# multiply by what on lose:
self.multiplier = 2.0
```

RUN
-------------

python just-dice-bot.py

LICENSE
-------------

GPLv2 applies. Please refer to this project:
https://github.com/KgBC/just-dice-bot

DONATE
-------------

Send your satoshi's to: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83
Thanks.

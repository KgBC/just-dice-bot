just-dice-bot
=============

Hi, this is a betting bot for just-dice.com. Feel free to use it under GPL. If you want to donate some Beer (BTC): 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83 Thanks.

HOW IT WORKS
-------------

Just-dice has no api. What is used here is remoting the website with selenium. The bot runs - in difference to other bots - in the command line. IMHO this is much more stable than a Greasemonkey-Script running in a browser itself.

WHY USE this bot?
-------------

* betting style: martingale, your own theme, whatever. 
  Let the bot do what your calculations say is right.
* RISK MANAGEMENT: most bots fail on that: you say, what your want to risk.
  e.g. bot could martingale (= win first bet no matter how many losses) for 3 rounds on 50/50
       on 4th to 30th round it could avoid big losses by losing a bit round by round. Losing sounds bad, but it allows winning more with less balance. 
* Profit: I cannot guarantee that you win, but if you do good settings your probabilities to win much are good :)
  There are examples in the config.py, and I will help you on settings if documentation doesn't help you.
* Logging and Graphing: You can see every single bet in the logfile, and a graph showing your balance changes is drawn while the bot is running.
* Continuity: Share some of your profits with me, and I keep updating the bot as needed and wanted. Good deal?
* Support: I'm around, usually within hours, maybe a day. Just file a ticket.

auto-tip
-------------

Here's the deal: I made the bot, which gathers you BTC. 
I'll support your as long as enough donations come in.
So if you win, the bot sends X percent (default: 1%) to me. 
Let the bot builder life :D We will have nice winnings together :)

Your part of the deal: leave the 'auto-tip' setting to 1 % (or more, what you think the bot is worth).
My part of the deal: I code, support, update, help you with the bot.
Fair? I say yes, decide yourself.

FEATURES
-------------

* Graphing: just watch the bets.png and see what's going on (more graphs and stats to come)
* Flexible betting: decide how you want to bet, combine different chances with different multiplyers, hi/lo-switching, small waiting bets for x losses.
  Just define your betting style/system.
* Respect Servers DDOS settings: don't get blocked
* runs on Linux (even on console) and Windows
* fast/direct developer support
* Logging: every single bet, every reconnect, it's all there and reviewable
* many more :)

INSTALL
-------------

It's tested on python 2.7 on linux, some tested on windows too.
I installed these:

```
aptitude install firefox xvfb xterm xserver-xephyr fvwm python-matplotlib python-numpy
xhost +
pip install selenium
pip install PyVirtualDisplay
pip install EasyProcess
```

On windows, install Python 2.7 and some libaries, Selenium and Firefox. Here in Detail:
```
* Python 2.7:
  Download and install http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi
* Requirements to run Selenium in python:
  We need some modules in python. 
  * First: setuptools and pip:
    Install http://www.lfd.uci.edu/~gohlke/pythonlibs/2ydk2k2o/setuptools-0.9.7.win32-py2.7.exe
	Install http://www.lfd.uci.edu/~gohlke/pythonlibs/2ydk2k2o/pip-1.4.win32-py2.7.exe
  * Selenium: 	http://docs.seleniumhq.org/download/
    #open a cmd box:
    Start menu - search for 'cmd' - open cmd.exe
    #in cmd type (and press Return after each line):
      #change to the dir where pip.exe is in, usually:
	  cd \python27\scripts
	  #install selenium module for python
      pip install -U selenium
  * For graphing we also need Matplotlib and NumPy, pick the right files for your system here:
    Matplotlib: http://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib
    NumPy:      http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
  * Firefox: 	
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

RUNNING
-------------

```python just-dice-bot.py```

It will show every bet with one line:
This is taken from my currently running bot:

    -24.8%luck round 42|B  1034/1:36:41: -0.00000011-l --- (04.5%) = 0.01343032 total. session: +0.00005180 (+0.00077151(+005.7%)/d)
    -22.7%luck round  0|B  1035/1:36:47: +0.00000252-l +++ (04.5%) = 0.01343284 total. session: +0.00005432 (+0.00080821(+006.0%)/d)
    
    from left to right:
    * -22.7%luck				:	luck percentage:
      			e.g. if we do 10 bets on 50% chance, we'll get 0%. -22.7% means, we had bad luck on the random numbers.
    * round  0					:	round number in betting system:	
      			the bot is playing your system as defined in config.py. this number gives the current round counting from the beginning of the system.
      			round 0 has a special meaning: the bot is waiting for a defined number of losses to occour before betting the system. 
    * B  1035					:	total bet number since bot start
    * 1:36:47					:	total runtime since bot start
    * +0.00000252				:	current win/lose (+/-)
    * -l						:	bet was lo (-l) or high (-h)
    * +++						:	we won (+++) or we lost (---)
    * (04.5%)					:	chance to win on this bet
    * = 0.01343284 total		:	total balance on just-dice
    * session: +0.00005180		:	balance changed since bot start
    * (+0.00077151(+005.7%)/d)	:	if we calculate the current winnings to one day, we would have +0.00077151 (which is +5.7% daily)
      Two optional parameters may occur:
    o max lost: -0.00001257		:	max. lost btc since last win (only shown if it's higher than ever before in this session)
    o max rows: 60				:	max. rows since last win (only shown if it's higher than ever before in this session)

A huge beginners error is watching at the percentage, and panic on -500% on third bet or so.
Why is that? Well, just after starting there is less data to calculate up to 24 hours.
So after starting with new settings, watch at the 'the total win in that session' (just before the word 'total').
You *may* lose some raffles, but should recover based on probabilities. So do your math (or try my defaults).

CONTROL THE APP IN CONSOLE:
* Please dont close the Firefox-Window or click there. The bot will try to recover from that error, but that will take time.
* Instead use this commands in console (they all need an ENTER to send the command):

	'q|quit'     : quit
	'h|?|help'   : this help
	's10'        : set safe_perc to 10 (0..100)
	               also resets the current safe balance
	's'          : get safe_perc and current safe balance
	'r25'        : set rounds to 25 (1..x)
	'r'          : get lose_rounds setting
	end all your commands with the ENTER key.
	
So if you want to stop, press "q<ENTER>" and wait for the bot to show stats and shutdown.

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

DONATE (Beer)
-------------

Send your satoshi's to: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83
Or even better: use auto-tip feature :)
Thanks.

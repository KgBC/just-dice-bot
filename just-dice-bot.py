#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple martingale bot for just-dice.com
Copyright (c) 2013 KgBC <IFGIWg@tormail.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import os, sys
import select

import logging
from logging.handlers import TimedRotatingFileHandler

if os.name != 'nt':
    from pyvirtualdisplay import Display
    from easyprocess import EasyProcess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time, re, math
from decimal import Decimal
from datetime import datetime, timedelta
import random
import traceback
import signal
from urllib2 import URLError

import sqlite3
from matplotlib.figure import Figure  # @UnresolvedImport
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas  # @UnresolvedImport        
import matplotlib.dates as mdates  # @UnresolvedImport

try:
    from config import jdb_config #this is your config
except:
    print "you have no working config.py. Please review README."
    sys.exit(20)

#stdin handling that works on windows and linux
from thread import start_new_thread
global commandlist
commandlist = []
def get_stdin_thread():
    global commandlist
    while True:
        try:
            commandlist.append( raw_input() )
        except EOFError:
            pass
start_new_thread(get_stdin_thread, ())
def get_stdin():
    global commandlist
    while True:
        try:
            cmd = commandlist.pop(0)
        except IndexError:
            break
        yield cmd

""" betting on just-dice """
class JustDice_impl():
    def __init__(self):
        self.fake_starttime = timedelta(seconds=0)
        self.ddos_last = datetime.utcnow()
    
    def setUp(self, visible, user, password):
        self.visible = visible
        self.user = user
        self.password = password
        
        if os.name != 'nt':
            self.display = Display(visible=visible,
                              size=(1024, 768))
            self.display.start()
            
            if visible:
                #window manager for resizable windows
                EasyProcess('fvwm').start()
                """
                def preexec_function():
                    # Ignore the SIGINT signal by setting the handler to the standard
                    # signal handler SIG_IGN.
                    signal.signal(signal.SIGINT, signal.SIG_IGN)
                subprocess.Popen(
                    ['fvwm'],
                    preexec_fn = preexec_function)
                """
        
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://just-dice.com"
        
    def do_login(self):
        try:
            self.driver.get(self.base_url + "/")
            #close fancy box (name)
            try:
                self.driver.find_element_by_css_selector("a.fancybox-item.fancybox-close").click()
            except: pass
            # login
            #time.sleep(3)
            self.driver.find_element_by_link_text("Account").click()
            self.driver.find_element_by_id("myuser").clear()
            self.driver.find_element_by_id("myuser").send_keys(self.user)
            self.driver.find_element_by_id("mypass").clear()
            self.driver.find_element_by_id("mypass").send_keys(self.password)
            #time.sleep(1)
            self.driver.find_element_by_id("myok").click()
            # get balance, login is OK when balance >= 0.00000001
            self.balance = self.get_balance()
            # show my bets
            self.driver.find_element_by_link_text("My Bets").click()
        except Exception as e:
            self.reconnect(e)
        
    def get_balance(self):
        try:
            for i in range(60*20):
                try:
                    balance_text = self.driver.find_element_by_id("pct_balance").get_attribute("value")
                    try: balance = float(balance_text)
                    except: balance = 0.0
                    if balance != 0.0:
                        return balance
                except: pass #is that a good idea? At least it will fail after 25s.
                time.sleep(.05)
        except Exception as e:
            self.reconnect(e)
        
        #timeout
        raise Exception('null balance, login error or selenium down')
        
    def do_bet(self, chance, bet, bet_hi):
        while True: #try again if something fails
            try:
                # bet: chance to win
                self.driver.find_element_by_id("pct_chance").clear()
                self.driver.find_element_by_id("pct_chance").send_keys("%4.2f" % chance)
                # bet: bet size
                self.driver.find_element_by_id("pct_bet").clear()
                self.driver.find_element_by_id("pct_bet").send_keys("%10.8f" % bet)
                #time.sleep(.5)
                if self.slow_bet:
                    print "doing bet with chance %s and bet %s. Press ENTER to continue (or wait 10s)." % ("%4.2f" % chance, "%10.8f" % bet)
                    #if select.select([sys.stdin], [], [], 10)[0]:
                    #    cmd = sys.stdin.readline()
                    for x in range(0,10):
                        if get_stdin():
                            #we continue
                            break
                        time.sleep(1)
                # sleep before bet: https://github.com/KgBC/just-dice-bot/issues/26
                if bet <= 9e-08:
                    #bets of 0.00000001 BTC to 0.00000009 BTC are delayed by 1 second
                    ddos_wait = timedelta(seconds=1.0)
                elif bet <= 99e-08:
                    #bets of 0.00000010 BTC to 0.00000099 BTC are delayed by 0.8 seconds
                    ddos_wait = timedelta(seconds=0.8)
                elif bet <= 999e-08:
                    #bets of 0.00000100 BTC to 0.00000999 BTC are delayed by 0.6 seconds
                    ddos_wait = timedelta(seconds=0.6)
                elif bet <= 9999e-08:
                    #bets of 0.00001000 BTC to 0.00009999 BTC are delayed by 0.4 seconds
                    ddos_wait = timedelta(seconds=0.4)
                elif bet <= 99999e-08:
                    #bets of 0.00010000 BTC to 0.00099999 BTC are delayed by 0.2 seconds
                    ddos_wait = timedelta(seconds=0.2)
                else: 
                    #bets of 0.00100000 BTC or more are not delayed
                    ddos_wait = timedelta(seconds=0.0)
                sleeptime = ( ddos_wait - (datetime.utcnow()-self.ddos_last) ).total_seconds()
                if sleeptime > 0.0:
                    time.sleep(sleeptime)
                self.ddos_last = datetime.utcnow()
                
                # BET: roll high or low on random
                if bet_hi:
                    hi_lo = "a_hi"
                else:
                    hi_lo = "a_lo"
                #check bet size before betting (#28 someone was typing some wrong value):
                if self.driver.find_element_by_id("pct_chance").get_attribute("value") != ("%4.2f" % chance):
                    raise Exception("canceling bet, chance value has changed")
                if self.driver.find_element_by_id("pct_bet").get_attribute("value") != ("%10.8f" % bet):
                    raise Exception("canceling bet, bet value has changed")
                #BET BET BET
                self.driver.find_element_by_id(hi_lo).click()
                
                # compare balance (timeout 10s)
                for i in range(200):
                    new_balance = self.get_balance()
                    if new_balance != self.balance:
                        saldo = new_balance-self.balance
                        self.balance = new_balance
                        return saldo
                    time.sleep(.05)
                #timeout - retry
                self.reconnect()
            except Exception as e:
                self.reconnect(e)
    
    def do_autotip(self, tip):
        while True:
            try:
                self.driver.find_element_by_id("a_withdraw").click()
                self.driver.find_element_by_id("wd_address").clear()
                self.driver.find_element_by_id("wd_address").send_keys("1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83")
                self.driver.find_element_by_id("wd_amount").clear()
                self.driver.find_element_by_id("wd_amount").send_keys("%s" % ("%0.8f" % tip,) )
                self.driver.find_element_by_id("wd_button").click()
            except Exception as e:
                self.reconnect(e)
        time.sleep(2)
        #error?
        try:
            err_text=""
            if   self.is_element_present(By.XPATH, "//div[@id='form_error']/p[2]"):
                err_text = self.driver.find_element_by_xpath("//div[@id='form_error']/p[2]").text
            elif self.is_element_present(By.CSS_SELECTOR, "#form_error > p"):
                err_text = self.driver.find_element_by_css_selector("#form_error > p").text
            return err_text
        except Exception as e:
            return "python error %s" % (e,)
    
    def tearDown(self):
        try:
            self.driver.quit()
        except: pass
        
        if os.name != 'nt':
            self.display.stop()
    
    def reconnect(self, err='timeout'):
        title = "No page title available"
        try:
            title = self.driver.title
        except: pass
        
        print 'reconnecting (trying fast method) T: %s E: %s' % (title, err,)
        logger.error( 'reconnect (fast) T: %s E: %s' % (title, err,) )
        
        try:
            self.driver.get(self.base_url + "/")
            self.driver.find_element_by_link_text("My Bets").click()
            time.sleep(2)
            return True
        except Exception as e:
            self.reconnect_slow(err)
    def reconnect_slow(self, err='timeout'):
        while True:
            print "reconnecting (be patient)"
            logger.error( 'reconnect %s' % (err,) )
            try:
                time.sleep(5)
                self.tearDown()
            except Exception as e:
                pass
            try:
                time.sleep(5)
                self.setUp(self.visible, self.user, self.password)
                self.do_login()
                return True
            except Exception as e:
                err = e
    
class Simulate_impl():
    def __init__(self, luck=0):
        #just dice will start with:
        self.balance = 100.0 #yes, 100btc. 
        #so, if we end up simulating X rounds we immediatly know win/lose in %
        self.fake_starttime = timedelta(seconds=3.5)
        self.__bets = 0
        self.__luck = luck

    def setUp(self, visible, user, password):
        self.visible = visible
        self.user = user
        self.password = password
    
    def do_login(self):
        pass
    
    def get_balance(self):
        return self.balance 
    
    def do_bet(self, chance, bet, bet_hi):
        #small gap for inputs, we do a minimum sleep every 10 bets
        self.__bets += 1
        if self.__bets % 100 == 0:
            time.sleep(0.1)
        #bet simulation
        saldo = -bet
        num = random.random()*(100+self.__luck)  #by x% unlucky
        #TODO: Simulate with hi/lo logic (bet_hi)
        #we always bet low
        if num < chance:
            #win
            payout_perc = 99.0/chance   #1% house edge
            saldo = bet*(payout_perc-1)
        else:
            #lose
            pass #already payed
        self.balance += saldo
        return saldo
    
    def do_autotip(self, tip):
        print "*** no auto-tip in simulation ***"
        return ""
    
    def tearDown(self):
        pass
    
    def reconnect(self, err='timeout'):
        raise Exception("whoaaa wait, why should I reconnect? I'm a simulator!")
    
class JustDiceBet():
    def get_conf(self, name, default):
        if jdb_config.has_key(name):
            return jdb_config[name]
        else: return default
    def get_conf_int(self, name, default):
        try: 
            i = int(self.get_conf(name, default))
            return i
        except ValueError:
            print "config.py: could not read %s config option as integer. Please review README."
            sys.exit(21)
    def get_conf_float(self, name, default):
        try: 
            f = float(self.get_conf(name, default))
            return f
        except ValueError:
            print "config.py: could not read %s config option as integer. Please review README."
            sys.exit(22)
    
    def __init__(self):
        print
        print "Simple martingale bot for just-dice.com"
        print "Copyright (C) 2013 KgBC <IFGIWg@tormail.org>"
        print "under GPLv2 (see source)"
        print
        print "News/new versions see https://github.com/KgBC/just-dice-bot"
        
        self.user = self.get_conf("user", "")
        self.password = self.get_conf("pass", "")
        #to debug we want a nicer output:
        self.visible = self.get_conf_int("visible", 0)
        self.lose_rounds = self.get_conf_int("lose_rounds", -1)
        self.chance = self.get_conf("chance", "") #self.get_conf_float("chance", -1.0)
        self.multiplier = self.get_conf("multiplier", "")
        self.safe_perc = self.get_conf_float("safe_perc", 0.0)
        self.autotip = self.get_conf_float("auto-tip", 1)
        self.min_bet = self.get_conf_float('min_bet', 1e-8)
        self.simulate = self.get_conf_int("simulate", -1)
        self.simulate_showevery = 1
        self.wait_loses = self.get_conf_int("wait_loses", 0)
        self.wait_chance= self.get_conf_float("wait_chance", 50.0)
        self.wait_bet   = self.get_conf_float("wait_bet", 1e-08)
        self.hi_lo      = self.get_conf("hi_lo", 'random')
        
        #luck %
        luck_estim = 0.0    #counting all luck we should have 
        luck_lucky = 0.0    #counting real luck
        
        #debug options:
        self.slow_bet = self.get_conf_int('slow_bet', 0)
        self.debug_issue_21 = self.get_conf('debug_issue_21', 0)
        
        #test settings
        if self.user=="":
            print "you need to specify a user name. See config.py"
            sys.exit(1)
        if self.password=="":
            print "you need to specify a password. See config.py"
            sys.exit(2)
        if not (0 <= self.visible <= 1):
            print "visible could be 1 or 0. See config.py"
            self.visible = 1
        if self.lose_rounds <= 0:
            print "lose_rounds must be a number > 0. See config.py"
            sys.exit(3)
        if not self.chance:
            print "a chance must be defined. See config.py"
            sys.exit(4)
        if not self.multiplier:
            print "a multiplyer must be defined. See config.py"
            sys.exit(5)
        if not (0.0 <= self.safe_perc < 100.0):
            print "safe_perc must be greater 0 and below 100. See config.py"
            sys.exit(6)
        if not (0.0 <= self.autotip <= 50.0): 
            print "auto-tip could be anything between 0 and 50 %. See config.py"
            self.autotip=50.0
        if not (0 <= self.slow_bet <= 1):
            print "slow_bet could be 1 or 0."
            self.slow_bet = 1
        if not (-1 <= self.simulate):
            print "simulate -1 for no simulaton, 0 for simulation, higher int for less luck in %. See config.py"
            self.simulate = -1 #live play default
            
        #do we accept a lose somewhere?
        self.maxlose_perc = 100.0 #we will lose all if we need to play more rounds as excpected.
        if type(self.multiplier) is list:
            last = self.multiplier[-1]
            if type(last) is str:
                if last.lower().startswith('lose'):
                    #check params:
                    if self.lose_rounds != len(self.multiplier):
                        print "you are using 'loseX' syntax in multiplyer, lose_rounds must match played rounds."
                        sys.exit(23)
                    try:
                        self.maxlose_perc = float(self.multiplier[-1][4:])
                    except:
                        print "multiplier error, loseX must be a number"
                        sys.exit(7)
                    if not 0.0 < self.maxlose_perc <= 100.0:
                        print "multiplyer: loseX must be greater 0 and below 100. See config.py"
                        sys.exit(8)
        
        #internal vars
        self.balance = 0.0
        self.safe_balance = 0.0
        self.total = 0.0
        self.max_lose = 0.0
        self.most_rows_lost = 0
        lost_sum = 0.0
        lost_rows = 0
        self.show_funds_warning = True
        self.loses_waited = 0
        
        #simulating?
        if self.simulate==-1:
            log_fn = "bets.log"
            graph_fn = "bets.png"
            #not simulating:
            self.remote_impl = JustDice_impl()
            banner = " playing on just-dice.com with real btc "
        else:
            log_fn = "bets-simulating.log"
            graph_fn = "bets-simulated.png"
            self.remote_impl = Simulate_impl( luck=self.simulate )
            banner = " fast, random simulating with 100btc (like %) "
        print
        print "#"*10 + banner + "#"*10
        time.sleep(3)
        
        global logHandler
        global logFormatter
        global logger
        logHandler = TimedRotatingFileHandler(log_fn, when="midnight")
        logFormatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s')
        logHandler.setFormatter( logFormatter )
        logger = logging.getLogger( 'MyLogger' )
        logger.addHandler( logHandler )
        logger.setLevel( logging.INFO )
        
        #temporary database
        self.db = sqlite3.connect('', isolation_level=None,
                                  detect_types=sqlite3.PARSE_DECLTYPES) #we want an temporary file based database
        self.db.execute("""
                CREATE TABLE IF NOT EXISTS bets
                    (dt TIMESTAMP, balance REAL);
                """)
        
        print
        print "Set up selenium (this will take a while, be patient) ..."
        self.setUp()
        print "Login (still be patient) ..."
        self.do_login()
        #empty stdin buffer
        for cmd in get_stdin():
            pass
        self.help()
        
        config_no_credentials = jdb_config
        config_no_credentials["user"] = '*'
        config_no_credentials["pass"] = '*'
        logger.info("starting with config: %s" % (repr(config_no_credentials),) )
        
        print "Start betting ..."
        self.starttime = datetime.utcnow()
        self.betcount  = 0
        #start betting
        bet = self.get_max_bet()
        self.run = True
        lost_rows = 0
        self.starting_balance = self.balance
        self.lowest_balance = self.balance
        self.highest_balance = self.balance
        while self.run:
            #import pydevd; pydevd.settrace('127.0.0.1')
            #bet
            try:
                warn = ''
                #prepare bet
                if self.loses_waited < self.wait_loses:
                    #waiting bet
                    chance = self.wait_chance
                    self.betcount += 1
                    bet = self.wait_bet
                else:
                    chance = self.get_chance(lost_rows)
                    self.betcount += 1
                    bet = self.get_rounded_bet(bet, chance)
                #are we below safe-balance? STOP
                if self.balance < self.safe_balance:
                    print "STOPPING, we would get below safe percentage in this round!"
                    print "safe_perc: %s%%, balance: %s, safe balance: %s" % (
                                  self.safe_perc, 
                                  "%+.8f" % self.balance,
                                  "%+.8f" % self.safe_balance)
                    self.run = False
                else:
                    #hi/lo strategy
                    if   self.hi_lo == 'random':
                        bet_hi = random.randint(0,1)
                    elif self.hi_lo == 'always_hi':
                        bet_hi = True
                    elif self.hi_lo == 'always_lo':
                        bet_hi = False
                    else:
                        raise Exception("hi_lo config option isn't implemented")
                    
                    #BET BET BET
                    saldo = self.do_bet(chance=chance, bet=bet, bet_hi=bet_hi)
                    #luck stats estimate
                    luck_estim += chance
                    if saldo > 0.0:
                        #win
                        bet = self.get_max_bet()
                        
                        #stats about losing
                        lost_sum = 0.0
                        lost_rows = 0
                        #luck stats - won
                        luck_lucky += 100.0
                        
                        #reset waited lost bets:
                        self.loses_waited = 0
                    else:
                        #lose:
                        
                        #are we waiting for lost bets?
                        if self.loses_waited < self.wait_loses:
                            self.loses_waited += 1
                            if self.loses_waited >= self.wait_loses:
                                bet = self.get_max_bet()
                                lost_rows = 0
                        else:
                            #lose, multiplyer for next round:
                            multi = self.get_multiplyer(lost_rows)
                            if multi == 'lose':
                                warn += ", we lose"
                                bet = self.get_max_bet()
                                lost_rows = 0
                            else:
                                bet = bet*multi
                                #next rounds vars
                                lost_rows += 1
                                lost_sum += saldo
                    
                    #add win/lose:
                    self.total += saldo
                    #warnings:
                    sim_show_warn = False
                    if lost_sum < self.max_lose:   #numbers are negative
                        self.max_lose = lost_sum
                        warn += ', max lost: %s' % ("%+.8f" % self.max_lose,)
                    if lost_rows > self.most_rows_lost:
                        self.most_rows_lost = lost_rows
                        warn += ', max rows: %s' % (self.most_rows_lost,)
                        sim_show_warn = True
                    
                    #total in 24 hours
                    now = datetime.utcnow()
                    difftime = (now-self.starttime)
                    day_sec = 24*60*60
                    difftime_sec = difftime.days*day_sec + difftime.seconds
                    win_24h = self.total*day_sec/difftime_sec
                    win_24h_percent = win_24h/self.balance*100
                    
                    #lowest/highest balance:
                    #self.starting_balance
                    if self.balance < self.lowest_balance:
                        self.lowest_balance = self.balance
                    if self.balance > self.highest_balance:
                        self.highest_balance = self.balance
                    
                    self.db.execute("""
                        INSERT INTO bets
                            VALUES (?, ?);
                        """, (now, self.balance) )
                    
                    bet_info = "%s%%luck round%s|B%s/%s: %s %s (%s%%) = %s total. session: %s (%s(%s%%)/d)%s" % (
                                       "%+6.1f" % (luck_lucky/luck_estim*100-100),
                                       "%3i"     % lost_rows,
                                       "%6i"     % self.betcount,
                                       str(difftime).split('.')[0],
                                       "%+.8f"   % saldo, 
                                       "WIN " if (saldo>=0) else "LOSE",
                                       "%04.1f"  % chance,
                                       "%0.8f"   % self.balance,
                                       "%+.8f"   % self.total,
                                       "%+.8f"   % win_24h,   #will be more as starting bet should raise
                                       "%+06.1f" % win_24h_percent,
                                       warn)
                    # when simulating print only every 100th bet info + bet's with warnings:
                    if self.simulate == -1:
                        print bet_info
                        logger.info(bet_info)
                    elif sim_show_warn:
                        print bet_info
                        logger.info(bet_info)
                    elif self.betcount % self.simulate_showevery == 0:
                        print bet_info
                        logger.info(bet_info)
                        
                    #graphing
                    if self.simulate == -1:
                        graph_every = 10 #not simulating, every 10 bets
                    else:
                        graph_every = 1000
                    
                    if self.betcount % graph_every == 0:
                        c = self.db.execute("""
                                    SELECT dt, balance 
                                    FROM bets;""")
                        data = c.fetchall()
                        if not data == None:
                            data_dt = []; data_bal = [];
                            for dt, bal in data:
                                data_dt.append(dt)
                                data_bal.append(bal)
                            #graph
                            fig    = Figure()
                            canvas = FigureCanvas(fig)
                            ax = fig.add_subplot(111)
                            fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')
                            ax.set_xlabel('Time', fontsize=10)
                            ax.set_ylabel('BTC', fontsize=10)
                            ax.plot(data_dt, data_bal, '-', color='r', label='balance')
                            #legend
                            handles, labels = ax.get_legend_handles_labels()
                            ax.legend(handles, labels, loc=2)
                            ax.grid(True)
                            #re-write files
                            if os.path.exists(graph_fn):
                                    os.unlink(graph_fn)
                            canvas.print_figure(graph_fn)
                            
                    
                    #read command line
                    #while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    #    cmd = sys.stdin.readline().rstrip('\n')
                    for cmd in get_stdin():
                        if   cmd.lower() in ['q','quit','exit']:
                            #quit
                            self.run = False
                        elif cmd.lower() in ['h','?','help']:
                            self.help()
                        elif cmd.lower().startswith('s'):
                            if cmd[1:]: #set
                                try:
                                    sp = int(cmd[1:])
                                    if sp<=100 and sp>=0:
                                        self.safe_perc = sp
                                        self.safe_balance = 0.0
                                        l = "resetting safe_perc, new value from now on: %s%%" % (sp,)
                                        print l
                                        logger.info(l)
                                except ValueError:
                                    print "command '%s' failed, keeping old safe_perc" % (cmd,)
                            else: #get
                                print "safe_perc is set to %s%%, which is currently %s" % (
                                               self.safe_perc, "%0.8f" % self.safe_balance)
                        elif cmd.lower().startswith('r'):
                            if cmd[1:]: #set
                                if self.maxlose_perc != 100:
                                    print "setting lose_rounds is disabled, incompatible with your multiplyer setting."
                                else:
                                    try:
                                        r = int(cmd[1:])
                                        if r>=0:
                                            self.lose_rounds = r
                                            l = "setting lose_rounds to: %s" % (r,)
                                            print l
                                            logger.info(l)
                                    except ValueError:
                                        print "command '%s' failed, keeping old lose_rounds" % (cmd,)
                            else: #get
                                print "lose_rounds is set to %s" % (self.lose_rounds,)
                        else:
                            print "command '%s' not found." % (cmd,)
                            self.help()
            except KeyboardInterrupt:
                self.run = False
            except Exception as e:
                print "Exception %s, retrying..." % (e,)
                print traceback.format_exc()
            
        #all bets done (with 'while True' this will never happen)
        print
        print "Starting balance     : %s" % ("%+.8f" % self.starting_balance,)
        print "Lowest   balance     : %s" % ("%+.8f" % self.lowest_balance,)
        print "Highest  balance     : %s" % ("%+.8f" % self.highest_balance,)
        print "Longest losing streak: %s rows" % (self.most_rows_lost,)
        print "Most expensive streak: %s" % ("%+.8f" % self.max_lose,)
        print 
        
        if self.total > 0.0:
            tip = (self.total/100*self.autotip) - 0.0001 #tip excluding fee.
            print "Congratulations, you won %s since %s (this session)" % (
                       "%+.8f" % self.total, 
                       str(difftime).split('.')[0] )
            if self.autotip==0:
                if not tip <= 0.0:
                    print "Why not tip 1%% = %s to the developer? 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83\nYou may also set 'auto-tip' in config.py. \nThanks!" % (
                              "%+.8f" % (self.total/100*1) )
            elif tip <= 0.0:
                print "You are using auto-tip feature, thanks. This time tip is too low because of fee's."
            else:
                print "You are using auto-tip feature, thanks. I would tip %s to the developer." % (
                           "%+.8f" % tip )
                s = 10
                print "If you want to cancel the tip, press Enter in next %ss. Also read documentation on auto-tip." % (s,)
                
                #while 
                #if sys.stdin in select.select([sys.stdin], [], [], s)[0]:
                cancel = False
                for x in range(0,s):
                    if get_stdin():
                        cancel = True
                if cancel:
                    cmd = sys.stdin.readline().rstrip('\n')
                    print "You decided to cancel my tip. You could also help the project by recommending it somewhere!\nShare this link: https://github.com/KgBC/just-dice-bot"
                else:
                    print "Starting auto-tip ..."
                    ret = self.do_autotip(tip)
                    if '1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83' in ret:
                        print "You auto-tip'ed. Thanks for your support! king regards, KgBC https://github.com/KgBC/just-dice-bot"
                    else:
                        print "Auto-tip failed, \nError from just-dice: %s\nPlease tip manually: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83" % (
                                       err,)
        else:
            print "You lost %s since %s (this session)\nYou know, it's betting, so losing is normal.\nYou may want to take less risk, see README: https://github.com/KgBC/just-dice-bot \nIf settings are unclear just file an issue on GitHub. I'll help. Thanks." % (
                       "%+.8f" % self.total, 
                       str(difftime).split('.')[0] )
        print
        print "Shutting down..."
        self.tearDown()
    
    def get_max_bet(self):
        #safe balance
        sb = self.balance / 100 * self.safe_perc
        if self.safe_balance < sb:
            self.safe_balance = sb
        
        #we want to lose after X rounds:
        r = self.lose_rounds
        b = (self.balance - self.safe_balance) /100*self.maxlose_perc
        
        #for bet rounding issues we keep 1%
        b = b*0.99
        
        #new method: simulate instead of calculate. 
        #  slightly slower, but easier and more flexible
        bet = b
        base = 1.0          #base for calculation
        used_base = 0.0     #bet amount we cumulate before a win
        #first bet is done without raise, so start with 2
        #last round is r, to include that round we stop with r+1
        for round in range(2,r+1):
            used_base += base
            multi = self.get_multiplyer(round-2)   #array pos 0 = round 2
            base = base*multi
            #print multi, base
        base += used_base
        #print base
        bet = bet/base
        bets_infos = "bets: "
        if bet < self.min_bet:
            if self.show_funds_warning:
                print "ATTENTION: we do not have enough funds to play your system defined in config.py. Choose:"
                print "    * ignore from now on and play it anyway:     ENTER"
                print "    * stop playing (and change system or funds): CTRL+C"
                while True:
                    if get_stdin():
                        #we continue
                        break
                    time.sleep(1)
            self.show_funds_warning = False #ignore
            bets_infos += "roundup from %s to " % (
                                 "%+.12f" % bet,)
            bet = self.min_bet
        bet_sim = bet
        bets_infos += "%s - " % ("%+.12f" % bet_sim,)
        for round in range(2, r+1):
            multi = self.get_multiplyer(round-2)   #array pos 0 = round 2
            bet_sim = bet_sim*multi
            bets_infos += "%s - " % ("%+.12f" % bet_sim,)
        bets_infos += "LOSE."
        logger.debug(bets_infos)
        return bet
    
    def setUp(self):
        self.remote_impl.setUp(self.visible, self.user, self.password)
    
    def do_login(self):
        self.remote_impl.do_login()
        try:
            self.balance = self.remote_impl.balance
        except AttributeError: # just in case balance isn't read
            self.balance = 0.0
    
    def get_balance(self):
        balance = self.remote_impl.get_balance()
        return balance
        
    def do_bet(self, chance, bet, bet_hi):
        self.remote_impl.slow_bet = self.slow_bet
        saldo = self.remote_impl.do_bet(chance, bet, bet_hi)
        self.balance = self.remote_impl.balance
        self.starttime = self.starttime - self.remote_impl.fake_starttime
        return saldo
        
    def do_autotip(self, tip):
        err_text = self.remote_impl.do_autotip(tip)
        return err_text
        
    def tearDown(self):
        self.remote_impl.tearDown()
            
    def reconnect(self, err='timeout'):
        success = self.remote_impl.reconnect(err)
        return success
        
    def get_rounded_bet(self, bet, chance):
        """
        if self.debug_issue_21: logger.info( 'issue21: chance=%s' % (chance,) )
        bet_base = math.ceil( (99.0/chance-1) *100)/100
        if self.debug_issue_21: logger.info( 'issue21: bet=%s, bet_base=%s' % (bet,bet_base,) )
        satoshi = bet/1e-08
        satoshi_rest = satoshi % bet_base
        if satoshi_rest: #we have a rest
            satoshi = math.ceil( satoshi - satoshi_rest + bet_base )
        rounded_bet = satoshi*1e-08
        if self.debug_issue_21: logger.info( 'issue21: rounded_bet=%s' % (rounded_bet,) )
        return rounded_bet
        """
        bet_satoshi = Decimal(str(bet))/Decimal("1e-08")
        chance = Decimal(str(chance))
        
        payout = Decimal("99.0")/chance
        payout_exactness = payout - Decimal( math.floor(payout) )
        if payout_exactness == Decimal("0"):
            #no rounding necessary
            return bet
        else:
            satoshi_multi = Decimal(1)/payout_exactness
            round_up_by = satoshi_multi - (bet_satoshi % satoshi_multi)
            bet_satoshi_rounded = bet_satoshi + round_up_by
            return float( bet_satoshi_rounded*Decimal("1e-08") )
    
    def get_chance(self, r):
        #we may have a list of round numbers:
        if type(self.chance) is list:
            if r >= len(self.chance):
                #return last chance for all other rows
                c = self.chance[-1]
            else:
                #return chance for round
                c = self.chance[r]
        else:
            c = self.chance
        #we have single chance, is it a formula?
        if type(c) is str:
            #is a formula, eval:
            c = 0.0+eval(c)
        #now we should have a float
        c = float(c)
        return c
    
    def get_multiplyer(self, r):
        #we may have a list of round numbers:
        if type(self.multiplier) is list:
            if r >= len(self.multiplier):
                #return last multiplyer for all other rows
                m = self.multiplier[-1]
            else:
                #return multiplyer for round
                m = self.multiplier[r]
        else:
            m = self.multiplier
        #we have single multiplyer, is it a formula?
        if type(m) is str:
            if m.lower().startswith('lose'):
                return 'lose'   #not convertible to a float :)
            else:
                #is a formula, eval:
                m = 0.0+eval(m)
        #now we should have a float
        m = float(m)
        return m
    
    def help(self):
        print "-"*120
        print "'q|quit'     : quit"
        print "'h|?|help'   : this help"
        print "'s10'        : set safe_perc to 10 (0..100)"
        print "               also resets the current safe balance"
        print "'s'          : get safe_perc and current safe balance"
        print "'r25'        : set rounds to 25 (1..x)"
        print "'r'          : get lose_rounds setting"
        print "end all your commands with the ENTER key."
        print "-"*120
    
    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

if __name__ == "__main__":
    JustDiceBet()

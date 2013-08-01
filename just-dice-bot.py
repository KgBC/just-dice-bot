#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple martingale bot for just-dice.com
Copyright (C) 2013 KgBC <IFGIWg@tormail.org>

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
logging.basicConfig(
            filename='bets.log',
            level=logging.INFO, 
            format='%(asctime)s, %(levelname)s: %(message)s'
            )

if os.name != 'nt':
    from pyvirtualdisplay import Display
    from easyprocess import EasyProcess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time, re, math
from datetime import datetime, timedelta
import random
import traceback
import signal

from config import jdb_config #this is your config

class JustDiceBet():
    def __init__(self):
        self.user = jdb_config["user"]
        self.password = jdb_config["pass"]
        #to debug we want a nicer output:
        self.visible = jdb_config["visible"]
        self.lose_rounds = int( jdb_config["lose_rounds"] )
        self.chance = float( jdb_config["chance"] )
        self.multiplier = jdb_config["multiplier"]
        self.safe_perc = jdb_config["safe_perc"]
        self.autotip = float( jdb_config["auto-tip"] )
        if self.autotip > 100.0: self.autotip=100.0
        
        #internal vars
        self.balance = 0.0
        self.safe_balance = 0.0
        self.total = 0.0
        self.max_lose = 0.0
        self.most_rows_lost = 0
        lost_sum = 0.0
        lost_rows = 0
        
        print
        print "Simple martingale bot for just-dice.com"
        print "Copyright (C) 2013 KgBC <IFGIWg@tormail.org>"
        print "under GPLv2 (see source)"
        print
        print "News/new versions see https://github.com/KgBC/just-dice-bot"
        
        print
        print "Set up selenium (this will take a while, be patient) ..."
        self.setUp()
        print "Login (still be patient) ..."
        self.do_login()
        self.help()
        
        print "Start betting ..."
        self.starttime = datetime.utcnow()
        #start betting
        bet = self.get_max_bet()
        self.run = True
        while self.run:
            #bet
            try:
                #bet
                saldo = self.do_bet(chance=self.chance, bet=bet)
                if saldo > 0.0:
                    #win
                    #bet=start_bet
                    bet = self.get_max_bet()
                    
                    #stats about losing
                    lost_sum = 0.0
                    lost_rows = 0
                else:
                    #lose
                    bet = bet*self.get_multiplyer(lost_rows)
                    #next rounds vars
                    lost_rows += 1
                    lost_sum += saldo
                    
                #win:
                self.total += saldo
                #warnings:
                warn = ''
                if lost_sum < self.max_lose:   #numbers are negative
                    self.max_lose = lost_sum
                    warn += ', max lost: %s' % ("%+.8f" % self.max_lose,)
                if lost_rows > self.most_rows_lost:
                    self.most_rows_lost = lost_rows
                    warn += ', max rows: %s' % (self.most_rows_lost,)
                
                #total in 24 hours
                difftime = (datetime.utcnow()-self.starttime)
                day_sec = 24*60*60
                difftime_sec = difftime.days*day_sec + difftime.seconds
                win_24h = self.total*day_sec/difftime_sec
                win_24h_percent = win_24h/self.balance*100
                
                bet_info = "%s: %s = %s: %s %s (%s(%s%%)/d)%s" % (
                                   str(difftime).split('.')[0],
                                   "%+.8f" % saldo, 
                                   "%0.8f" % self.balance,
                                   "%+.8f" % self.total,
                                   "WIN " if (saldo>=0) else "LOSE",
                                   "%+.8f" % win_24h,   #will be more as starting bet should raise
                                   "%+.1f" % win_24h_percent,
                                   warn)
                print bet_info
                logging.info(bet_info)
                #read command line
                while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    cmd = sys.stdin.readline().rstrip('\n')
                    if   cmd.lower() in ['q','quit','exit']:
                        #quit
                        self.run = False
                    elif cmd.lower() in ['h','?','help']:
                        self.help()
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
        if self.total > 0.0:
            tip = (self.total/100*self.autotip) - 0.0001 #tip excluding fee.
            print "Congratulations, you won %s since %s (this session)" % (
                       "%+.8f" % self.total, 
                       str(difftime).split('.')[0] )
            if self.autotip==0:
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
                if sys.stdin in select.select([sys.stdin], [], [], s)[0]:
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
        b = self.balance - self.safe_balance
        
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
        if bet < 1e-08:
            print "calculated starting bet: %s, betting %s" % (
                       "%+.12f" % bet, "%+.8f" % 1e-08)
            bet = 1e-08
        #raise Exception('STOP')
        return bet
        
    def setUp(self):
        if os.name != 'nt':
            self.display = Display(visible=self.visible,
                              size=(1024, 768))
            self.display.start()
            
            if self.visible:
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
        self.driver.implicitly_wait(15)
        self.base_url = "https://just-dice.com"
        
    #def test_just_dice_recorded(self):
    def do_login(self):
        self.driver.get(self.base_url + "/")
        #close fancy box (name)
        self.driver.find_element_by_css_selector("a.fancybox-item.fancybox-close").click()
        # login
        self.driver.find_element_by_link_text("Account").click()
        self.driver.find_element_by_id("myuser").clear()
        self.driver.find_element_by_id("myuser").send_keys(self.user)
        self.driver.find_element_by_id("mypass").clear()
        self.driver.find_element_by_id("mypass").send_keys(self.password)
        self.driver.find_element_by_id("myok").click()
        # get balance, login is OK when balance >= 0.00000001
        self.balance = self.get_balance()
        # show my bets
        self.driver.find_element_by_link_text("My Bets").click()
        
    def get_balance(self):
        for i in range(30):
            balance_text = self.driver.find_element_by_id("pct_balance").get_attribute("value")
            try: balance = float(balance_text)
            except: balance = 0.0
            if balance != 0.0:
                return balance
            time.sleep(1)
        #timeout
        raise Exception('null balance or login error')
        
    def do_bet(self, chance, bet):
        # bet: chance to win
        self.driver.find_element_by_id("pct_chance").clear()
        self.driver.find_element_by_id("pct_chance").send_keys("%4.2f" % chance)
        # bet: bet size
        self.driver.find_element_by_id("pct_bet").clear()
        self.driver.find_element_by_id("pct_bet").send_keys("%10.8f" % bet)
        time.sleep(.5)
        # roll high or low on random
        if random.randint(0,1):
            hi_lo = "a_hi"
        else:
            hi_lo = "a_lo"
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
        return 0.0
        
    def get_multiplyer(self, r):
        #we may have a list of round numbers:
        if type(self.multiplier) is list:
            if r >= len(self.multiplier):
                #return last multiplyer for all other rows
                m = self.multiplier[-1]
            else:
                #return multiplyer for round
                m = self.multiplier[r]
        #we have single multiplyer, is it a formula?
        if type(m) is str:
            #is a formula, eval:
            m = 0.0+eval(m)
        #now we should have a float
        return m
    
    def do_autotip(self, tip):
        self.driver.find_element_by_id("a_withdraw").click()
        self.driver.find_element_by_id("wd_address").clear()
        self.driver.find_element_by_id("wd_address").send_keys("1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83")
        self.driver.find_element_by_id("wd_amount").clear()
        self.driver.find_element_by_id("wd_amount").send_keys("%s" % ("%0.8f" % tip,) )
        self.driver.find_element_by_id("wd_button").click()
        time.sleep(2)
        #error?
        err_text=""
        if   self.is_element_present(By.XPATH, "//div[@id='form_error']/p[2]"):
            err_text = self.driver.find_element_by_xpath("//div[@id='form_error']/p[2]").text
        elif self.is_element_present(By.CSS_SELECTOR, "#form_error > p"):
            err_text = self.driver.find_element_by_css_selector("#form_error > p").text
        return err_text
    
    def tearDown(self):
        try:
            self.driver.quit()
        except: pass
        
        if os.name != 'nt':
            self.display.stop()
            
    def help(self):
        print "--- press 'q|quit' to quit, 'h|?|help' for command help ---"
        print "---       finish your commands with the ENTER key       ---"
    
    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

if __name__ == "__main__":
    JustDiceBet()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple martingale bot for just-dice.com
Copyright (C) 2013 KgBC <>

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

import os

if os.name != 'nt':
    from pyvirtualdisplay import Display
    from easyprocess import EasyProcess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

import time, re, math

class JustDiceBet():
    def __init__(self):
        #to debug we want a nicer output:
        #self.visible = 1
        self.visible = 0
        self.lose_rounds = 25
        self.chance=49.5
        self.multiplier = 2.0
        
        self.balance = 0.0        
        self.setUp()
        self.do_login()
        #start betting
        bet = self.get_max_bet()
        while True: #for bet_count in range(100):
            try:
                #bet
                saldo = self.do_bet(chance=self.chance, bet=bet)
                print "%s = %s" % ("%+.8f" % saldo, 
                                   "%0.8f" % self.balance)
                if saldo > 0.0:
                    #win
                    #bet=start_bet
                    bet = self.get_max_bet()
                else:
                    #lose, multiply
                    bet=bet*self.multiplier
            except KeyboardInterrupt:
                break
        #all bets done (with 'while True' this will never happen)
        self.tearDown()
        
    def get_max_bet(self):
        #we want to lose after X rounds:
        r = float(self.lose_rounds)
        b = float(self.balance)
        bet = math.floor( 
                     ( b*pow(2,-r) )*1e+08
                 )*1e-08
        if bet < 1e-08:
            bet = 1e-08
        return bet
        
    def setUp(self):
        if os.name != 'nt':
            self.display = Display(visible=self.visible,
                              size=(1024, 768))
            self.display.start()
            
            if self.visible:
                #window manager for resizable windows
                EasyProcess('fvwm').start()
        
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://just-dice.com"
        
    #def test_just_dice_recorded(self):
    def do_login(self):
        self.driver.get(self.base_url + "/")
        # close welcome box
        for i in range(30):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "div.welcome"): break
            except: pass
            time.sleep(1)
        else: pass
        self.driver.find_element_by_css_selector("a.fancybox-item.fancybox-close").click()
        # login
        self.driver.find_element_by_link_text("Account").click()
        self.driver.find_element_by_id("myuser").clear()
        self.driver.find_element_by_id("myuser").send_keys("Hg6ILk")
        self.driver.find_element_by_id("mypass").clear()
        self.driver.find_element_by_id("mypass").send_keys("5oGeRmsPzdsK72JWh3gt")
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
        raise Exception('null balance')
        
    def do_bet(self, chance, bet):
        # bet: chance to win
        self.driver.find_element_by_id("pct_chance").clear()
        self.driver.find_element_by_id("pct_chance").send_keys("%4.2f" % chance)
        # bet: bet size
        self.driver.find_element_by_id("pct_bet").clear()
        self.driver.find_element_by_id("pct_bet").send_keys("%10.8f" % bet)
        time.sleep(.5)
        # roll high
        self.driver.find_element_by_id("a_hi").click()
        # compare balance
        for i in range(300):
            new_balance = self.get_balance()
            if new_balance != self.balance:
                saldo = new_balance-self.balance
                self.balance = new_balance
                return saldo
            time.sleep(.05)
        #timeout
        raise Exception('bet was unsuccessful')
        
    def tearDown(self):
        self.driver.quit()
        
        if os.name != 'nt':
            self.display.stop()

if __name__ == "__main__":
    JustDiceBet()

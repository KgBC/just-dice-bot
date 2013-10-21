#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The trick is, to find the configuration which brings you MOST profit, BUT is not too RISKY
# Here are two example configs, let me explain them to you.

# For those who want to test immediatly: read the comments on the first example, you dont get all the details,
# but all that is needed for first experiments. But you know where to search if needed :)
# For those in hurry: jump to ----------------------------- SHORT DESCRIPTION ----------------------------- 

#----------------------------- FULL DESCRIPTION -----------------------------
# variables ordered by importance: 
# * multiplyer  : multipy by X on lose. 
#                 multiplyer could be a number like e.g. 2.0 to double on every lost round.
#                 multiplyer could also be a python list, with a multiplyer for each round (example below)
#                     in case of the list, LAST value is duplicated to match the length of lose_rounds (see next param)
#                 no matter if it's a list or a single value: it might also be a eval()-string if you know python.
#                 multiplyer could also be 'loseXX', where XX is a percentage to lose at the current round. example below.
#                     in this case 'lose_rounds' must match.
# * lose_rounds : is used to calculate the starting bet. How?
#                 Lets do a simple example: we double on every loss (which means multiplyer: 2.0)
#                 We set lose_rounds to 4 (which is much too low, we need to survive more losses, but it's easier to explain)
#                 Lets again think of a balance with 0.1 Bitcoins
#                 The bot calculates: 0.1 btc /2 = 0.05 /2 = 0.025 /2 = 0.125 /2 = 0.00625 btc.
#                 in this example, the first bet will be 0.00625.
#                 THIS is recalculated (better: simulated) after every win
#                 IF the start bet is lower than 0.00000001 we bet exactly 0.00000001.
#                 see also: safe_perc
# * chance      : chance to win percentage we set for bets. This may also be a python list if we want to use different chances in the betting system
# * safe_perc   : percent of the balance *not used* in first bet calculations.
#                 this is ALWAYS calculated from the highest balance we owned. 
#                 so if we got 10 BTC, and lose 1 BTC, it's still x % from 10 BTC.
# * visible     : on linux you may run the firefox-window inside an xvfb (X virtual framebuffer). Needed to run on console only.
#                 It's faster than running a visible instance and you cannot mistakenly type on the open window.
#                 use '"visible" : 1' for testing, and switch it to '"visible" : 0' later.
# * user/pass   : your just-dice user and password. Never give them to anyone.
# * simulate    : simulate your system. very useful for testing without risking your money.
#                 Simulating always starts at 100 BTC, so you could see all BTC values as percentages :)
#                 We also try to estimate run times, so simulating some minutes could lead to test data usually handled on JD in days :)
#                 '"simulate" : 0' is the default, which means we quickly simulate with about 0% luck.
#                 use a positive number here to simulate with bader luck, e.g. '"simulate" : -3' will give you about 3 more losses in 100.
#                 Simulating is not exactly as playing on JD, e.g. the hi/lo-switching is not implemented yet. This will follow soon.
# * wait_loses  : before starting the system defined in chance and multiplyer, do X waiting bets, at ...
#   wait_chance : ... this chance, and with ...
#   wait_bet    : ... this value. Some say it might be better to wait some losses before betting high.
#                 While waiting, you'll lose around 1% house edge. 
# * hi_lo"      : you can choose if you want to bet hi or low. Possible values are:
#                 switch_on_win:    switch hi/lo after a win
#                 random:           choose ranomly every round (just-dice couldn't guess that, so thats the default)
#                 always_hi:        always bet hi
#                 always_lo:        always bet lo
#                 more to come in later versions, see: https://github.com/KgBC/just-dice-bot/issues/27#issuecomment-26030993
# 
# * auto-tip    : It's all about money: I made a bot for you, you will probably WIN money with this bot if used correctly.
#                 I don't want to cash you for that promise - I want you to test the bot. 
#                 If it gives you profit (as it should) donate to me. Just pay me as much as you think the bot is worth.
#                 Here is the deal of auto-tip: you set this to a percentage, e.g. 1%, and as soon as you stop the bot 
#                 it will send me 1% of every win you have. There is also a delay, where you could cancel it anyway.
#                 I for my part guarantee, as long as money flows it I will update this bot and make it even better.
#                 Sure: if you lose, you dont pay.
#                 Good deal? Then leave it at 1 (for 1%). Thanks.

#----------------------------- SHORT DESCRIPTION -----------------------------
# this is a very safe standard martingale system.
jdb_config = {
    "visible"    : 1,					#1 = show selenium browser automation (slower, but you see what happens, dont use in productive)
    "user"       : "YOUR_USER",			#your user and password on just-dice
    "pass"       : "YOUR_PASSWORD",
    "lose_rounds": 30,					#bet, so that we could lose for X rounds. Minimum bet is 0.00000001.
    "chance"     : 49.5,				#which chance do we want to bet on
    "multiplier" : 2.0,					#multiply bet by X on lose
    "safe_perc"  : 5.0,                 #percent of balance is NOT used for first bet calculation
    "auto-tip"   : 1,                   #IMPORTANT: 
                                        #This is my deal: I made the bot, which gathers you BTC. 
                                        #I'll support your as long as enough donations come in.
                                        #So if you win, the bot sends X percent (default: 1%) to me. 
                                        #Let the bot builder life :D We will have nice winnings together :)
}

# raise less, win more per round (but don't win all losses every round)
#jdb_config = {
#    "visible"    : 1,
#    "user"       : "YOUR_USER",
#    "pass"       : "YOUR_PASSWORD",
#    "lose_rounds": 27,
#    "chance"     : 49.5,
#    "multiplier" :                           #rounds
#            [ 3.0, 2.5, 2.0]+                #0,1,2 maximizes win
#            [ 1.75 for x in range( 3, 7)]+   #3-6   win less every round
#            [ 1.5  for x in range( 7,13)]+   #7-12  win less every round
#            [ 1.1],                          # -lose_rounds covers parts of the loss
#    "safe_perc"  : 5.0,
#    "auto-tip"   : 1,
#}

# just another variant for settings:
# you know, we are in python here. so we could code: see that multiplyer:
# raise less, win more per round (but don't win all losses every round)
#jdb_config = {
#    "visible"    : 1,
#    "user"       : "YOUR_USER",
#    "pass"       : "YOUR_PASSWORD",
#    "lose_rounds": 25,
#    "chance"     : 49.5,
#    "multiplier" : 
#            [ 2.5, 2.5, 2.5]+           
#            [(10.0-x)/10+1 for x in range(0,10)],
#    "safe_perc"  : 5.0,
#    "auto-tip"   : 1,
#}
# if you want to know, what '[ 2.5, 2.5, 2.5]+ [(10.0-x)/10+1 for x in range(0,10)]' means, 
# fire up a python shell and paste:
#In [1]: [ 2.5, 2.5, 2.5]+ [(10.0-x)/10+1 for x in range(0,10)]
#Out[1]: [2.5, 2.5, 2.5, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1]
#see? python as we love it (well some of us :D)

#another variant: 'lose' after some rounds, and start from starting bet again:
# needs testing, see https://github.com/KgBC/just-dice-bot/issues/9#issuecomment-21992305
#jdb_config = {
#    "visible"    : 0,
#    "user"       : "YOUR_USER",
#    "pass"       : "YOUR_PASSWORD",
#    "chance"     : 49.5,
#    "lose_rounds": 6,
#    "multiplier" : 
#            [ 2.0, 2.0, 2.0, 2.0, 2.0, 'lose5' ],   
#                        #lose5 this accepts loss after 6 rounds and starts with a new first bet.
#                        #it uses 5% of (balance*safe_perc%). multiplier must match!
#    "safe_perc"  : 5.0,
#    "auto-tip"   : 1,
#}

#new feature: different chances per round
#jdb_config = {
#    "visible"    : 1,
#    "user"       : "YOUR_USER",
#    "pass"       : "YOUR_PASSWORD",
#    "min_bet"    : 0.00000002,      #minimum bet 2 satoshi
#    "lose_rounds": 8,               #do 8 rounds
#    "multiplier" : [      11.0,],   #multiply bet by 11 every round
#    "chance"     : [49.5, 90.0,],   #first round with 49,5% chance, 2nd to 8th round with 90% chance
#    "safe_perc"  : 10.0,
#    "auto-tip"   : 1,
#}

# a low budget example:
# we expect 230 losing rounds max (if we lose them we will lose 50%)
# we start betting higher after 30 rounds
#rounds = 200
#wait   = 230 - rounds   #we do not risk much on the first 30 rounds (minimum bet there)
#jdb_config = {
#    "visible"    : 1,
#    "user"       : "YOUR_USER",
#    "pass"       : "YOUR_PASSWORD",
#    "lose_rounds": rounds,                 #max 230 rounds to lose ...
#    "chance"     : 4.5,                    #... on a 4.5 % chance
#    "multiplier" : [     1.05 for x in range(0,rounds-1)] + ['lose50'],    #after that we'll lose 50%
#    "safe_perc"  : 0,
#    "auto-tip"   : 1,
#    #"simulate"   : 0,
#    "wait_loses" : wait,                   #these are the waiting bets, 30 bets ...
#    "wait_chance": 4.5,                    #... on a 4.5 % chance also ...
#    "wait_bet"   : 1e-08,                  #... only betting 0.00000001 BTC (no matter what the balance is)
#    "hi_lo"      : 'switch_on_win',        #and we want to switch from hi to low on win (or from lo to hi)
#}

### ah yes, remember:
### leave auto-tip on, or buy me some beer if you win, and I'll continue development :) Thanks!
### bitcoin-address: 1CDjWb7zupTfQihc6sMeDvPmUHkfeMhC83
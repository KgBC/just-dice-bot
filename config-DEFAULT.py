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
# * lose_rounds : is used to calculate the starting bet. How?
#                 Lets do a simple example: we double on every loss (which means multiplyer: 2.0)
#                 We set lose_rounds to 4 (which is much too low, we need to survive more losses, but it's easier to explain)
#                 Lets again think of a balance with 0.1 Bitcoins
#                 The bot calculates: 0.1 btc /2 = 0.05 /2 = 0.025 /2 = 0.125 /2 = 0.00625 btc.
#                 in this example, the first bet will be 0.00625.
#                 THIS is recalculated (better: simulated) after every win
#                 IF the start bet is lower than 0.00000001 we bet exactly 0.00000001.
#                 see also: safe_perc
# * chance      : chance to win percentage we set for bets
# * safe_perc   : percent of the balance *not used* in first bet calculations.
#                 this is ALWAYS calculated from the highest balance we owned. 
#                 so if we got 10 BTC, and lose 1 BTC, it's still x % from 10 BTC.
# * auto-tip    : It's all about money: I made a bot for you, you will probably WIN money with this bot if used correctly.
#                 I don't want to cash you for that promise - I want you to test the bot. 
#                 If it gives you profit (as it should) donate to me. Just pay me as much as you think the bot is worth.
#                 Here is the deal of auto-tip: you set this to a percentage, e.g. 1%, and as soon as you stop the bot 
#                 it will send me 1% of every win you have. There is also a delay, where you could cancel it anyway.
#                 I for my part guarantee, as long as money flows it I will update this bot and make it even better.
#                 Sure: if you lose, you dont pay.
#                 Good deal? Then leave it at 1 (for 1%). Thanks.

#    btw: I made 0.01383437 just in that 2,5 hours I wrote that text above.
#         I used the second setting here which is commented out ... So have fun making money :)
#         see: 2:24:50: +0.00046639 = 0.19927649: +0.01383437 WIN  (+0.13754771(+69.0%)/d)

#----------------------------- SHORT DESCRIPTION -----------------------------
# this is a very safe standard martingale system.
jdb_config = {
    "visible"    : 1,					#1 = show selenium browser automation (slower, but you see what happens, dont use in productive)
    "user"       : "YOUR_USER",			#your user and password on just-dice
    "pass"       : "YOUR_PASSWORD",
    "lose_rounds": 30,					#bet, so that we could lose for X rounds. Minimum bet is 0.00000001.
    "chance"     : 49.5,				#which chance do we want to bet on
    "multiplier" : 2.0					#multiply bet by X on lose
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

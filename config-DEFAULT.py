#!/usr/bin/env python
# -*- coding: utf-8 -*-

jdb_config = {
    "visible"    : 1,					#1 = show selenium browser automation (slower, but you see what happens)
    "user"       : "YOUR_USER",			#your user and password on just-dice
    "pass"       : "YOUR_PASSWORD",
    "lose_rounds": 30,					#bet, so that we could lose for X rounds. Minimum bet is 0.00000001.
    "chance"     : 49.5,				#which chance do we have
    "multiplier" : 2.0					#multiply bet by X on lose
}
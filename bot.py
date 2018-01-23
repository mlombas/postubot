#   This is the main file of the bot   
# 
#   Copyright (C) 2018  mocoma
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from secrets import *
import time
import tweepy

#variables
TIMEBETWEENTWEETS = 60 * 60

def getTwitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    return tweepy.API(auth)

#for a test, send a tweet every hour
while True:
    getTwitter().update_status(status = input("enter tweet to send: "))
    print("sent")

    time.sleep(TIMEBETWEENTWEETS)